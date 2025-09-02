import * as SQLite from 'expo-sqlite';
import { Platform } from 'react-native';

export interface OfflineAction {
  id: string;
  type: 'clock_in' | 'clock_out' | 'inventory_check' | 'purchase_order' | 'sync_data';
  data: any;
  timestamp: string;
  retry_count: number;
  max_retries: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
}

export interface LocalAttendance {
  id: string;
  user_id: number;
  type: 'in' | 'out';
  lat: number;
  lng: number;
  timestamp: string;
  synced: boolean;
  server_id?: number;
}

export interface LocalInventoryCheck {
  id: string;
  user_id: number;
  barcode: string;
  quantity: number;
  photo_url?: string;
  timestamp: string;
  synced: boolean;
  server_id?: number;
}

export interface LocalPurchaseOrder {
  id: string;
  user_id: number;
  branch_id: string;
  items: any[];
  total_amount: number;
  timestamp: string;
  synced: boolean;
  server_id?: number;
}

export class LocalStorageService {
  private static instance: LocalStorageService;
  private db: SQLite.SQLiteDatabase | null = null;

  private constructor() {}

  public static getInstance(): LocalStorageService {
    if (!LocalStorageService.instance) {
      LocalStorageService.instance = new LocalStorageService();
    }
    return LocalStorageService.instance;
  }

  /**
   * 데이터베이스 초기화
   */
  async initialize(): Promise<void> {
    try {
      this.db = await SQLite.openDatabaseAsync('mobile_app.db');
      await this.createTables();
      console.log('로컬 데이터베이스 초기화 완료');
    } catch (error) {
      console.error('로컬 데이터베이스 초기화 실패:', error);
      throw error;
    }
  }

  /**
   * 테이블 생성
   */
  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    // 오프라인 액션 큐 테이블
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS offline_actions (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        retry_count INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 3,
        status TEXT DEFAULT 'pending',
        error_message TEXT
      );
    `);

    // 로컬 출퇴근 기록 테이블
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS local_attendance (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        timestamp TEXT NOT NULL,
        synced INTEGER DEFAULT 0,
        server_id INTEGER
      );
    `);

    // 로컬 재고 조사 테이블
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS local_inventory_checks (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        barcode TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        photo_url TEXT,
        timestamp TEXT NOT NULL,
        synced INTEGER DEFAULT 0,
        server_id INTEGER
      );
    `);

    // 로컬 발주 테이블
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS local_purchase_orders (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        branch_id TEXT NOT NULL,
        items TEXT NOT NULL,
        total_amount REAL NOT NULL,
        timestamp TEXT NOT NULL,
        synced INTEGER DEFAULT 0,
        server_id INTEGER
      );
    `);

    // 로컬 사용자 데이터 테이블
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS local_user_data (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        data_type TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        synced INTEGER DEFAULT 0
      );
    `);
  }

  /**
   * 오프라인 액션 추가
   */
  async addOfflineAction(action: Omit<OfflineAction, 'id' | 'timestamp' | 'retry_count' | 'status'>): Promise<string> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    const id = `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = new Date().toISOString();

    await this.db.runAsync(
      `INSERT INTO offline_actions (id, type, data, timestamp, max_retries, status) 
       VALUES (?, ?, ?, ?, ?, 'pending')`,
      [id, action.type, JSON.stringify(action.data), timestamp, action.max_retries]
    );

    return id;
  }

  /**
   * 대기 중인 오프라인 액션 조회
   */
  async getPendingActions(): Promise<OfflineAction[]> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    const result = await this.db.getAllAsync(
      `SELECT * FROM offline_actions 
       WHERE status = 'pending' AND retry_count < max_retries 
       ORDER BY timestamp ASC`
    );

    return result.map(row => ({
      id: row.id as string,
      type: row.type as OfflineAction['type'],
      data: JSON.parse(row.data as string),
      timestamp: row.timestamp as string,
      retry_count: row.retry_count as number,
      max_retries: row.max_retries as number,
      status: row.status as OfflineAction['status'],
      error_message: row.error_message as string | undefined,
    }));
  }

  /**
   * 오프라인 액션 상태 업데이트
   */
  async updateActionStatus(id: string, status: OfflineAction['status'], errorMessage?: string): Promise<void> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    if (status === 'failed') {
      await this.db.runAsync(
        `UPDATE offline_actions 
         SET status = ?, error_message = ?, retry_count = retry_count + 1 
         WHERE id = ?`,
        [status, errorMessage || '', id]
      );
    } else {
      await this.db.runAsync(
        `UPDATE offline_actions 
         SET status = ?, error_message = ? 
         WHERE id = ?`,
        [status, errorMessage || '', id]
      );
    }
  }

  /**
   * 완료된 오프라인 액션 삭제
   */
  async deleteCompletedAction(id: string): Promise<void> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    await this.db.runAsync(
      `DELETE FROM offline_actions WHERE id = ? AND status = 'completed'`,
      [id]
    );
  }

  /**
   * 로컬 출퇴근 기록 저장
   */
  async saveLocalAttendance(attendance: Omit<LocalAttendance, 'id' | 'synced'>): Promise<string> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    const id = `attendance_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    await this.db.runAsync(
      `INSERT INTO local_attendance (id, user_id, type, lat, lng, timestamp, synced) 
       VALUES (?, ?, ?, ?, ?, ?, 0)`,
      [id, attendance.user_id, attendance.type, attendance.lat, attendance.lng, attendance.timestamp]
    );

    return id;
  }

  /**
   * 로컬 출퇴근 기록 조회
   */
  async getLocalAttendance(userId: number, limit: number = 50): Promise<LocalAttendance[]> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    const result = await this.db.getAllAsync(
      `SELECT * FROM local_attendance 
       WHERE user_id = ? 
       ORDER BY timestamp DESC 
       LIMIT ?`,
      [userId, limit]
    );

    return result.map(row => ({
      id: row.id as string,
      user_id: row.user_id as number,
      type: row.type as 'in' | 'out',
      lat: row.lat as number,
      lng: row.lng as number,
      timestamp: row.timestamp as string,
      synced: Boolean(row.synced),
      server_id: row.server_id as number | undefined,
    }));
  }

  /**
   * 로컬 재고 조사 저장
   */
  async saveLocalInventoryCheck(inventory: Omit<LocalInventoryCheck, 'id' | 'synced'>): Promise<string> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    const id = `inventory_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    await this.db.runAsync(
      `INSERT INTO local_inventory_checks (id, user_id, barcode, quantity, photo_url, timestamp, synced) 
       VALUES (?, ?, ?, ?, ?, ?, 0)`,
      [id, inventory.user_id, inventory.barcode, inventory.quantity, inventory.photo_url || '', inventory.timestamp]
    );

    return id;
  }

  /**
   * 로컬 발주 저장
   */
  async saveLocalPurchaseOrder(order: Omit<LocalPurchaseOrder, 'id' | 'synced'>): Promise<string> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    const id = `order_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    await this.db.runAsync(
      `INSERT INTO local_purchase_orders (id, user_id, branch_id, items, total_amount, timestamp, synced) 
       VALUES (?, ?, ?, ?, ?, ?, 0)`,
      [id, order.user_id, order.branch_id, JSON.stringify(order.items), order.total_amount, order.timestamp]
    );

    return id;
  }

  /**
   * 동기화되지 않은 데이터 조회
   */
  async getUnsyncedData(): Promise<{
    attendance: LocalAttendance[];
    inventory: LocalInventoryCheck[];
    orders: LocalPurchaseOrder[];
  }> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    const [attendanceResult, inventoryResult, ordersResult] = await Promise.all([
      this.db.getAllAsync(`SELECT * FROM local_attendance WHERE synced = 0`),
      this.db.getAllAsync(`SELECT * FROM local_inventory_checks WHERE synced = 0`),
      this.db.getAllAsync(`SELECT * FROM local_purchase_orders WHERE synced = 0`),
    ]);

    return {
      attendance: attendanceResult.map(row => ({
        id: row.id as string,
        user_id: row.user_id as number,
        type: row.type as 'in' | 'out',
        lat: row.lat as number,
        lng: row.lng as number,
        timestamp: row.timestamp as string,
        synced: Boolean(row.synced),
        server_id: row.server_id as number | undefined,
      })),
      inventory: inventoryResult.map(row => ({
        id: row.id as string,
        user_id: row.user_id as number,
        barcode: row.barcode as string,
        quantity: row.quantity as number,
        photo_url: row.photo_url as string | undefined,
        timestamp: row.timestamp as string,
        synced: Boolean(row.synced),
        server_id: row.server_id as number | undefined,
      })),
      orders: ordersResult.map(row => ({
        id: row.id as string,
        user_id: row.user_id as number,
        branch_id: row.branch_id as string,
        items: JSON.parse(row.items as string),
        total_amount: row.total_amount as number,
        timestamp: row.timestamp as string,
        synced: Boolean(row.synced),
        server_id: row.server_id as number | undefined,
      })),
    };
  }

  /**
   * 데이터 동기화 완료 표시
   */
  async markAsSynced(table: string, id: string, serverId?: number): Promise<void> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    const serverIdClause = serverId ? ', server_id = ?' : '';
    const params = serverId ? [1, serverId, id] : [1, id];

    await this.db.runAsync(
      `UPDATE ${table} SET synced = 1${serverIdClause} WHERE id = ?`,
      params
    );
  }

  /**
   * 데이터베이스 정리 (오래된 완료된 액션 삭제)
   */
  async cleanup(): Promise<void> {
    if (!this.db) throw new Error('데이터베이스가 초기화되지 않았습니다.');

    const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();

    await this.db.runAsync(
      `DELETE FROM offline_actions 
       WHERE status = 'completed' AND timestamp < ?`,
      [oneWeekAgo]
    );
  }
}

// 싱글톤 인스턴스 내보내기
export const localStorageService = LocalStorageService.getInstance();
