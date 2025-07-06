// 모든 Store를 한 곳에서 export
export { useStaffStore } from './useStaffStore';
export { useOrderStore } from './useOrderStore';
export { useInventoryStore } from './useInventoryStore';
export { useScheduleStore } from './useScheduleStore';

// 타입들도 함께 export
export type { StaffMember, Contract, HealthCertificate } from './useStaffStore';
export type { Order } from './useOrderStore';
export type { InventoryItem, StockMovement } from './useInventoryStore';
export type { Schedule, ShiftRequest } from './useScheduleStore'; 