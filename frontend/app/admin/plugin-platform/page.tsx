"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { 
  Smartphone, Tablet, Monitor, Globe, Settings, 
  Languages, Palette, SmartphoneIcon, CheckCircle, 
  XCircle, Loader2, RefreshCw, Eye, Code, 
  SmartphoneIcon as MobileIcon, MonitorIcon as DesktopIcon
} from "lucide-react";

const dummyPlugins = [
  {
    id: 1,
    name: "ai_schedule_optimizer",
    display_name: "AI 스케줄 최적화",
    supported_platforms: ["web", "mobile", "tablet"],
    current_platform: "web",
    ui_schema: {
      web: { layout: "sidebar", components: ["header", "sidebar", "content"] },
      mobile: { layout: "stacked", components: ["header", "content", "navigation"] },
      tablet: { layout: "grid", components: ["sidebar", "content", "toolbar"] }
    }
  },
  {
    id: 2,
    name: "review_auto_summary",
    display_name: "리뷰 자동 요약",
    supported_platforms: ["web", "mobile"],
    current_platform: "mobile",
    ui_schema: {
      web: { layout: "sidebar", components: ["header", "sidebar", "content"] },
      mobile: { layout: "stacked", components: ["header", "content", "navigation"] }
    }
  },
  {
    id: 3,
    name: "qsc_analyzer",
    display_name: "QSC 분석기",
    supported_platforms: ["web", "tablet", "pos"],
    current_platform: "pos",
    ui_schema: {
      web: { layout: "sidebar", components: ["header", "sidebar", "content"] },
      tablet: { layout: "grid", components: ["sidebar", "content", "toolbar"] },
      pos: { layout: "touch", components: ["header", "content", "keypad"] }
    }
  }
];

const platformConfigs = {
  web: {
    icon: DesktopIcon,
    label: "웹",
    description: "데스크톱 및 노트북 브라우저",
    features: ["전체 기능", "키보드 지원", "마우스 인터랙션"],
    limitations: []
  },
  mobile: {
    icon: MobileIcon,
    label: "모바일",
    description: "스마트폰 앱 및 브라우저",
    features: ["터치 최적화", "제스처 지원", "오프라인 지원"],
    limitations: ["파일 업로드 제한", "고급 분석 제한"]
  },
  tablet: {
    icon: Tablet,
    label: "태블릿",
    description: "태블릿 앱 및 브라우저",
    features: ["터치 최적화", "분할 화면", "펜 지원"],
    limitations: ["데스크톱 기능 제한"]
  },
  pos: {
    icon: Smartphone,
    label: "POS",
    description: "포인트 오브 세일 터미널",
    features: ["터치 최적화", "바코드 스캔", "영수증 출력"],
    limitations: ["고급 기능 제한", "터치 전용"]
  }
};

const deviceSupport = {
  smartphone: {
    os: ["iOS", "Android"],
    browsers: ["Chrome", "Safari", "Firefox"],
    min_requirements: { ram: "2GB", storage: "1GB", resolution: "320x568" }
  },
  tablet: {
    os: ["iOS", "Android"],
    browsers: ["Chrome", "Safari", "Firefox"],
    min_requirements: { ram: "4GB", storage: "2GB", resolution: "768x1024" }
  },
  desktop: {
    os: ["Windows", "macOS", "Linux"],
    browsers: ["Chrome", "Firefox", "Safari", "Edge"],
    min_requirements: { ram: "8GB", storage: "5GB", resolution: "1920x1080" }
  },
  pos_terminal: {
    os: ["Windows Embedded", "Linux"],
    browsers: ["Chrome", "Firefox"],
    min_requirements: { ram: "4GB", storage: "8GB", resolution: "1024x768" }
  }
};

const languageOptions = [
  { code: "ko", name: "한국어", flag: "🇰🇷" },
  { code: "en", name: "English", flag: "🇺🇸" },
  { code: "ja", name: "日本語", flag: "🇯🇵" },
  { code: "zh", name: "中文", flag: "🇨🇳" },
  { code: "es", name: "Español", flag: "🇪🇸" },
  { code: "fr", name: "Français", flag: "🇫🇷" }
];

export default function AdminPluginPlatformPage() {
  const [plugins, setPlugins] = useState(dummyPlugins);
  const [selectedPlugin, setSelectedPlugin] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [platformSettings, setPlatformSettings] = useState({
    web_enabled: true,
    mobile_enabled: true,
    tablet_enabled: true,
    pos_enabled: false
  });
  const [uiSchema, setUISchema] = useState({
    layout: "responsive",
    components: [],
    navigation: {},
    themes: {}
  });
  const [selectedLanguages, setSelectedLanguages] = useState(["ko", "en"]);
  const [saving, setSaving] = useState(false);

  const tabs = [
    { id: "overview", label: "플랫폼 개요", icon: Globe },
    { id: "platforms", label: "플랫폼 설정", icon: Settings },
    { id: "ui", label: "UI 스키마", icon: Code },
    { id: "devices", label: "디바이스 지원", icon: Smartphone },
    { id: "languages", label: "다국어 설정", icon: Languages },
  ];

  const handlePlatformToggle = (platform: string, enabled: boolean) => {
    setPlatformSettings(prev => ({
      ...prev,
      [`${platform}_enabled`]: enabled
    }));
    
    toast.success(`${platformConfigs[platform].label} 플랫폼이 ${enabled ? '활성화' : '비활성화'}되었습니다.`);
  };

  const handleUISchemaUpdate = (field: string, value: any) => {
    setUISchema(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLanguageToggle = (languageCode: string) => {
    setSelectedLanguages(prev => {
      if (prev.includes(languageCode)) {
        return prev.filter(lang => lang !== languageCode);
      } else {
        return [...prev, languageCode];
      }
    });
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success("플랫폼 설정이 저장되었습니다!");
    } catch (error) {
      toast.error("설정 저장 중 오류가 발생했습니다.");
    } finally {
      setSaving(false);
    }
  };

  const handlePreviewPlatform = (platform: string) => {
    toast.info(`${platformConfigs[platform].label} 플랫폼 미리보기를 시작합니다.`);
  };

  return (
    <div className="container mx-auto p-6 max-w-7xl space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">플러그인 플랫폼 관리</h1>
        <Button
          onClick={handleSaveSettings}
          disabled={saving}
          className="flex items-center gap-2"
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Settings className="h-4 w-4" />}
          설정 저장
        </Button>
      </div>

      {/* 탭 네비게이션 */}
      <div className="flex border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              activeTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* 플랫폼 개요 탭 */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* 플랫폼 지원 현황 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {Object.entries(platformConfigs).map(([platform, config]) => {
              const Icon = config.icon;
              const supportedCount = plugins.filter(p => 
                p.supported_platforms.includes(platform)
              ).length;
              
              return (
                <Card key={platform}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{config.label}</CardTitle>
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{supportedCount}</div>
                    <p className="text-xs text-muted-foreground">
                      지원 플러그인 수
                    </p>
                    <div className="mt-2">
                      <Badge variant="outline" className="text-xs">
                        {config.description}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* 플러그인별 플랫폼 지원 */}
          <Card>
            <CardHeader>
              <CardTitle>플러그인별 플랫폼 지원 현황</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {plugins.map((plugin) => (
                  <div key={plugin.id} className="border rounded p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-semibold">{plugin.display_name}</h3>
                        <div className="text-sm text-muted-foreground">
                          현재 플랫폼: {platformConfigs[plugin.current_platform]?.label || plugin.current_platform}
                        </div>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedPlugin(plugin.id)}
                      >
                        설정
                      </Button>
                    </div>
                    
                    <div className="flex gap-2">
                      {Object.entries(platformConfigs).map(([platform, config]) => {
                        const isSupported = plugin.supported_platforms.includes(platform);
                        const Icon = config.icon;
                        
                        return (
                          <Badge
                            key={platform}
                            variant={isSupported ? "default" : "secondary"}
                            className="flex items-center gap-1"
                          >
                            <Icon className="h-3 w-3" />
                            {config.label}
                            {isSupported && <CheckCircle className="h-3 w-3" />}
                          </Badge>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 플랫폼 설정 탭 */}
      {activeTab === "platforms" && (
        <div className="space-y-6">
          {Object.entries(platformConfigs).map(([platform, config]) => {
            const Icon = config.icon;
            
            return (
              <Card key={platform}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Icon className="h-6 w-6" />
                      <div>
                        <CardTitle>{config.label}</CardTitle>
                        <p className="text-sm text-muted-foreground">{config.description}</p>
                      </div>
                    </div>
                    <Switch
                      checked={platformSettings[`${platform}_enabled`]}
                      onCheckedChange={(enabled) => handlePlatformToggle(platform, enabled)}
                    />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-2">지원 기능</h4>
                      <ul className="space-y-1">
                        {config.features.map((feature, index) => (
                          <li key={index} className="flex items-center gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">제한사항</h4>
                      <ul className="space-y-1">
                        {config.limitations.length > 0 ? (
                          config.limitations.map((limitation, index) => (
                            <li key={index} className="flex items-center gap-2 text-sm">
                              <XCircle className="h-4 w-4 text-red-500" />
                              {limitation}
                            </li>
                          ))
                        ) : (
                          <li className="text-sm text-muted-foreground">제한사항 없음</li>
                        )}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handlePreviewPlatform(platform)}
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      미리보기
                    </Button>
                    <Button size="sm" variant="outline">
                      <Code className="h-4 w-4 mr-2" />
                      UI 스키마
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* UI 스키마 탭 */}
      {activeTab === "ui" && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>UI 스키마 설정</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="layout">레이아웃 타입</Label>
                  <Select
                    value={uiSchema.layout}
                    onValueChange={(value) => handleUISchemaUpdate('layout', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="responsive">반응형</SelectItem>
                      <SelectItem value="sidebar">사이드바</SelectItem>
                      <SelectItem value="stacked">스택형</SelectItem>
                      <SelectItem value="grid">그리드</SelectItem>
                      <SelectItem value="touch">터치 최적화</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="components">컴포넌트 구성</Label>
                  <Textarea
                    id="components"
                    placeholder="컴포넌트 JSON 설정"
                    value={JSON.stringify(uiSchema.components, null, 2)}
                    onChange={(e) => {
                      try {
                        const parsed = JSON.parse(e.target.value);
                        handleUISchemaUpdate('components', parsed);
                      } catch (error) {
                        // JSON 파싱 오류 무시
                      }
                    }}
                    rows={6}
                  />
                </div>

                <div>
                  <Label htmlFor="themes">테마 설정</Label>
                  <Textarea
                    id="themes"
                    placeholder="테마 JSON 설정"
                    value={JSON.stringify(uiSchema.themes, null, 2)}
                    onChange={(e) => {
                      try {
                        const parsed = JSON.parse(e.target.value);
                        handleUISchemaUpdate('themes', parsed);
                      } catch (error) {
                        // JSON 파싱 오류 무시
                      }
                    }}
                    rows={4}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 디바이스 지원 탭 */}
      {activeTab === "devices" && (
        <div className="space-y-6">
          {Object.entries(deviceSupport).map(([device, support]) => (
            <Card key={device}>
              <CardHeader>
                <CardTitle className="capitalize">{device.replace('_', ' ')} 지원</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <h4 className="font-medium mb-2">운영체제</h4>
                    <div className="space-y-1">
                      {support.os.map((os) => (
                        <Badge key={os} variant="outline" className="mr-1">
                          {os}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-2">브라우저</h4>
                    <div className="space-y-1">
                      {support.browsers.map((browser) => (
                        <Badge key={browser} variant="outline" className="mr-1">
                          {browser}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-2">최소 요구사항</h4>
                    <div className="text-sm space-y-1">
                      <div>RAM: {support.min_requirements.ram}</div>
                      <div>저장공간: {support.min_requirements.storage}</div>
                      <div>해상도: {support.min_requirements.resolution}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* 다국어 설정 탭 */}
      {activeTab === "languages" && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>지원 언어 설정</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {languageOptions.map((language) => (
                  <div
                    key={language.code}
                    className={`border rounded p-4 cursor-pointer transition-colors ${
                      selectedLanguages.includes(language.code)
                        ? 'border-primary bg-primary/5'
                        : 'border-muted'
                    }`}
                    onClick={() => handleLanguageToggle(language.code)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{language.flag}</span>
                        <div>
                          <div className="font-medium">{language.name}</div>
                          <div className="text-sm text-muted-foreground">{language.code}</div>
                        </div>
                      </div>
                      {selectedLanguages.includes(language.code) && (
                        <CheckCircle className="h-5 w-5 text-primary" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6">
                <Label htmlFor="default-language">기본 언어</Label>
                <Select defaultValue="ko">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {selectedLanguages.map((langCode) => {
                      const language = languageOptions.find(l => l.code === langCode);
                      return (
                        <SelectItem key={langCode} value={langCode}>
                          {language?.flag} {language?.name}
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
} 