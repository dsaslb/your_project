import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { 
  Brain, 
  Zap, 
  Settings, 
  Play, 
  Pause, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  DollarSign,
  Users,
  Package,
  RefreshCw,
  Eye,
  BarChart3,
  Gauge,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface DecisionRule {
  rule_id: string;
  name: string;
  category: string;
  conditions: Array<{
    metric: string;
    operator: string;
    value: any;
    threshold: number;
  }>;
  actions: Array<{
    type: string;
    parameters: Record<string, any>;
  }>;
  priority: number;
  is_active: boolean;
  created_at: string;
  last_executed?: string;
}

interface AutomatedDecision {
  decision_id: string;
  rule_id: string;
  rule_name: string;
  category: string;
  trigger_data: Record<string, any>;
  decision_result: Record<string, any>;
  confidence: number;
  executed_actions: Array<Record<string, any>>;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
}

interface BusinessAction {
  action_id: string;
  action_type: string;
  parameters: Record<string, any>;
  estimated_impact: Record<string, any>;
  cost: number;
  priority: string;
  status: 'pending' | 'approved' | 'rejected' | 'executed';
  created_at: string;
  executed_at?: string;
}

interface DecisionStatus {
  active_decisions: number;
  pending_actions: number;
  system_config: Record<string, any>;
  recent_decisions: Array<{
    decision_id: string;
    rule_name: string;
    category: string;
    status: string;
    confidence: number;
    created_at: string;
  }>;
  action_queue_summary: {
    total_actions: number;
    action_types: Record<string, number>;
  };
}

const CATEGORY_COLORS = {
  inventory: '#3b82f6',
  pricing: '#10b981',
  staffing: '#f59e0b',
  marketing: '#ef4444',
  operations: '#8b5cf6'
};

const CATEGORY_ICONS = {
  inventory: Package,
  pricing: DollarSign,
  staffing: Users,
  marketing: TrendingUp,
  operations: Settings
};

const STATUS_COLORS = {
  pending: '#6b7280',
  executing: '#3b82f6',
  completed: '#10b981',
  failed: '#ef4444'
};

const AutomatedDecisionDashboard: React.FC = () => {
  const [decisionStatus, setDecisionStatus] = useState<DecisionStatus | null>(null);
  const [decisionRules, setDecisionRules] = useState<DecisionRule[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    fetchAutomatedDecisionData();
    const interval = setInterval(fetchAutomatedDecisionData, 30000); // 30초마다 업데이트
    return () => clearInterval(interval);
  }, []);

  const fetchAutomatedDecisionData = async () => {
    try {
      setIsLoading(true);
      setError('');

      // 의사결정 상태 조회
      const statusResponse = await fetch('/api/automated-decision/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        if (statusData.success) {
          setDecisionStatus(statusData);
        }
      }

      // 의사결정 규칙 조회
      const rulesResponse = await fetch('/api/automated-decision/rules', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (rulesResponse.ok) {
        const rulesData = await rulesResponse.json();
        if (rulesData.success) {
          setDecisionRules(rulesData.rules);
        }
      }

      setLastUpdate(new Date().toLocaleString());
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRule = async (ruleId: string) => {
    try {
      const response = await fetch(`/api/automated-decision/rules/${ruleId}/toggle`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // 규칙 목록 새로고침
          fetchAutomatedDecisionData();
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '규칙 토글 실패');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'executing': return <Activity className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'failed': return <AlertTriangle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  if (isLoading && !decisionStatus) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p>자동화된 의사결정 데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">자동화된 의사결정 대시보드</h1>
          <p className="text-muted-foreground">
            AI 기반 자동 의사결정 및 실행 시스템
          </p>
          <p className="text-sm text-muted-foreground">
            마지막 업데이트: {lastUpdate}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={fetchAutomatedDecisionData}
            disabled={isLoading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
        </div>
      </div>

      {/* 시스템 상태 요약 */}
      {decisionStatus && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-4 h-4" />
                활성 의사결정
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {decisionStatus.active_decisions}개
              </div>
              <div className="text-sm text-muted-foreground">
                현재 처리 중
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                대기 중인 액션
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {decisionStatus.pending_actions}개
              </div>
              <div className="text-sm text-muted-foreground">
                실행 대기 중
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gauge className="w-4 h-4" />
                자동 실행 임계값
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatPercentage(decisionStatus.system_config.approval_threshold)}
              </div>
              <div className="text-sm text-muted-foreground">
                신뢰도 기준
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                시스템 상태
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  decisionStatus.system_config.auto_execution_enabled 
                    ? 'bg-green-500' 
                    : 'bg-red-500'
                }`} />
                <span className="font-medium">
                  {decisionStatus.system_config.auto_execution_enabled 
                    ? '자동 실행 활성화' 
                    : '수동 모드'}
                </span>
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                자동화 상태
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 액션 큐 요약 */}
      {decisionStatus && decisionStatus.action_queue_summary.total_actions > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              액션 큐 현황
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(decisionStatus.action_queue_summary.action_types).map(([type, count]) => (
                <div key={type} className="text-center p-3 border rounded-lg">
                  <div className="text-lg font-bold">{count}</div>
                  <div className="text-sm text-muted-foreground capitalize">
                    {type.replace('_', ' ')}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 최근 의사결정 */}
      {decisionStatus && decisionStatus.recent_decisions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-4 h-4" />
              최근 의사결정
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {decisionStatus.recent_decisions.map((decision) => {
                const CategoryIcon = CATEGORY_ICONS[decision.category as keyof typeof CATEGORY_ICONS] || Brain;
                return (
                  <div key={decision.decision_id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <CategoryIcon className="w-4 h-4" />
                        <span className="font-medium">{decision.rule_name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge 
                          style={{ backgroundColor: STATUS_COLORS[decision.status as keyof typeof STATUS_COLORS] }}
                          className="text-white"
                        >
                          {decision.status}
                        </Badge>
                        {getStatusIcon(decision.status)}
                      </div>
                    </div>
                    <div className="flex items-center gap-4 mb-2">
                      <div className="flex items-center gap-1">
                        <span className="text-xs">신뢰도:</span>
                        <span className="text-sm font-medium">{formatPercentage(decision.confidence)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-xs">카테고리:</span>
                        <span className="text-sm font-medium capitalize">{decision.category}</span>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      생성: {new Date(decision.created_at).toLocaleString()}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 의사결정 규칙 관리 */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">전체</TabsTrigger>
          <TabsTrigger value="inventory">재고</TabsTrigger>
          <TabsTrigger value="pricing">가격</TabsTrigger>
          <TabsTrigger value="staffing">인력</TabsTrigger>
          <TabsTrigger value="marketing">마케팅</TabsTrigger>
          <TabsTrigger value="operations">운영</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {decisionRules.map((rule) => (
              <DecisionRuleCard 
                key={rule.rule_id} 
                rule={rule} 
                onToggle={toggleRule}
              />
            ))}
          </div>
        </TabsContent>

        {['inventory', 'pricing', 'staffing', 'marketing', 'operations'].map((category) => (
          <TabsContent key={category} value={category} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {decisionRules
                .filter(rule => rule.category === category)
                .map((rule) => (
                  <DecisionRuleCard 
                    key={rule.rule_id} 
                    rule={rule} 
                    onToggle={toggleRule}
                  />
                ))}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};

interface DecisionRuleCardProps {
  rule: DecisionRule;
  onToggle: (ruleId: string) => void;
}

const DecisionRuleCard: React.FC<DecisionRuleCardProps> = ({ rule, onToggle }) => {
  const CategoryIcon = CATEGORY_ICONS[rule.category as keyof typeof CATEGORY_ICONS] || Brain;
  
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CategoryIcon className="w-4 h-4" />
            <span className="text-sm">{rule.name}</span>
          </div>
          <Switch
            checked={rule.is_active}
            onCheckedChange={() => onToggle(rule.rule_id)}
          />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <Badge 
            style={{ backgroundColor: CATEGORY_COLORS[rule.category as keyof typeof CATEGORY_COLORS] }}
            className="text-white text-xs"
          >
            {rule.category}
          </Badge>
          <span className="text-xs text-muted-foreground">
            우선순위: {rule.priority}
          </span>
        </div>
        
        <div className="space-y-2">
          <div className="text-xs font-medium">조건:</div>
          <div className="space-y-1">
            {rule.conditions.map((condition, index) => (
              <div key={index} className="text-xs text-muted-foreground p-2 bg-muted rounded">
                {condition.metric} {condition.operator} {condition.value}
              </div>
            ))}
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="text-xs font-medium">액션:</div>
          <div className="space-y-1">
            {rule.actions.map((action, index) => (
              <div key={index} className="text-xs text-muted-foreground p-2 bg-muted rounded">
                {action.type}: {Object.keys(action.parameters).join(', ')}
              </div>
            ))}
          </div>
        </div>
        
        <div className="text-xs text-muted-foreground">
          생성: {new Date(rule.created_at).toLocaleDateString()}
          {rule.last_executed && (
            <div>마지막 실행: {new Date(rule.last_executed).toLocaleDateString()}</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default AutomatedDecisionDashboard; 