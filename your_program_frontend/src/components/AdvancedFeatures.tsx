'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient } from '@/lib/api-client';
import { useUser } from '@/hooks/useUser';
import { 
  MessageSquare, 
  Mic, 
  MicOff, 
  Image, 
  Languages, 
  Send,
  Upload,
  Download,
  Play,
  Square,
  Brain,
  Zap
} from 'lucide-react';

interface ChatMessage {
  message: string;
  response: string;
  intent: string;
  timestamp: string;
}

interface VoiceCommand {
  text: string;
  command_type: string;
  response: string;
  confidence: number;
}

interface ImageAnalysis {
  analysis_type: string;
  results: any;
  confidence: number;
}

interface TranslationResult {
  translated_text: string;
  confidence: number;
  processing_time: number;
}

const AdvancedFeatures: React.FC = () => {
  const { user } = useUser();
  const [activeTab, setActiveTab] = useState('chatbot');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 챗봇 상태
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);

  // 음성 인식 상태
  const [isRecording, setIsRecording] = useState(false);
  const [voiceResult, setVoiceResult] = useState<VoiceCommand | null>(null);
  const [audioData, setAudioData] = useState<string | null>(null);

  // 이미지 분석 상태
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imageAnalysis, setImageAnalysis] = useState<ImageAnalysis[]>([]);
  const [analysisTypes, setAnalysisTypes] = useState(['qr_code', 'ocr', 'quality']);

  // 번역 상태
  const [translateText, setTranslateText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [translationResult, setTranslationResult] = useState<TranslationResult | null>(null);

  // 오디오 관련 refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // 지원 언어
  const supportedLanguages = {
    'ko': '한국어',
    'en': 'English',
    'ja': '日本語',
    'zh': '中文',
    'es': 'Español',
    'fr': 'Français'
  };

  // 챗봇 메시지 전송
  const sendChatMessage = async () => {
    if (!chatMessage.trim()) return;

    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.post('/api/advanced/chatbot/message', {
        message: chatMessage
      });

      const newMessage: ChatMessage = {
        message: chatMessage,
        response: response.data.response,
        intent: response.data.intent,
        timestamp: response.data.timestamp
      };

      setChatHistory(prev => [...prev, newMessage]);
      setChatMessage('');
    } catch (err: any) {
      setError(err.response?.data?.error || '챗봇 메시지 전송에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 음성 녹음 시작
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const reader = new FileReader();
        reader.onload = async () => {
          const base64Audio = (reader.result as string).split(',')[1];
          await processVoiceCommand(base64Audio);
        };
        reader.readAsDataURL(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError('마이크 접근 권한이 필요합니다.');
    }
  };

  // 음성 녹음 중지
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  // 음성 명령 처리
  const processVoiceCommand = async (audioData: string) => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.post('/api/advanced/voice/process', {
        audio_data: audioData
      });

      setVoiceResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || '음성 처리에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 이미지 파일 선택
  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  // 이미지 분석
  const analyzeImage = async () => {
    if (!selectedImage) return;

    try {
      setLoading(true);
      setError(null);

      const reader = new FileReader();
      reader.onload = async () => {
        const base64Image = (reader.result as string).split(',')[1];
        
        const response = await apiClient.post('/api/advanced/image/analyze', {
          image_data: base64Image,
          analysis_types: analysisTypes
        });

        setImageAnalysis(response.data.results);
      };
      reader.readAsDataURL(selectedImage);
    } catch (err: any) {
      setError(err.response?.data?.error || '이미지 분석에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 텍스트 번역
  const handleTranslateText = async () => {
    if (!translateText.trim()) return;

    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.post('/api/advanced/translate/text', {
        text: translateText,
        target_language: targetLanguage
      });

      setTranslationResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || '번역에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">고급 기능</h1>
          <p className="text-muted-foreground">
            AI 챗봇, 음성 인식, 이미지 분석, 실시간 번역
          </p>
        </div>
        <Badge variant="outline" className="flex items-center gap-2">
          <Brain className="h-4 w-4" />
          AI Powered
        </Badge>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="chatbot" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            AI 챗봇
          </TabsTrigger>
          <TabsTrigger value="voice" className="flex items-center gap-2">
            <Mic className="h-4 w-4" />
            음성 인식
          </TabsTrigger>
          <TabsTrigger value="image" className="flex items-center gap-2">
            <Image className="h-4 w-4" />
            이미지 분석
          </TabsTrigger>
          <TabsTrigger value="translation" className="flex items-center gap-2">
            <Languages className="h-4 w-4" />
            실시간 번역
          </TabsTrigger>
        </TabsList>

        {/* AI 챗봇 */}
        <TabsContent value="chatbot" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI 챗봇</CardTitle>
              <CardDescription>
                자연어로 주문, 문의, 도움말을 받아보세요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 채팅 히스토리 */}
              <div className="h-64 overflow-y-auto border rounded-lg p-4 space-y-2">
                {chatHistory.map((msg, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-end">
                      <div className="bg-blue-500 text-white rounded-lg px-3 py-2 max-w-xs">
                        {msg.message}
                      </div>
                    </div>
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg px-3 py-2 max-w-xs">
                        {msg.response}
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 text-center">
                      의도: {msg.intent}
                    </div>
                  </div>
                ))}
              </div>

              {/* 메시지 입력 */}
              <div className="flex gap-2">
                <Input
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder="메시지를 입력하세요..."
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                />
                <Button onClick={sendChatMessage} disabled={loading}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 음성 인식 */}
        <TabsContent value="voice" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>음성 인식</CardTitle>
              <CardDescription>
                음성으로 주문하고 명령을 내려보세요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 음성 녹음 버튼 */}
              <div className="flex justify-center">
                <Button
                  size="lg"
                  variant={isRecording ? "destructive" : "default"}
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={loading}
                  className="w-20 h-20 rounded-full"
                >
                  {isRecording ? <MicOff className="h-8 w-8" /> : <Mic className="h-8 w-8" />}
                </Button>
              </div>

              <div className="text-center text-sm text-gray-500">
                {isRecording ? "녹음 중... (클릭하여 중지)" : "클릭하여 녹음 시작"}
              </div>

              {/* 음성 결과 */}
              {voiceResult && (
                <div className="space-y-2 p-4 border rounded-lg">
                  <div>
                    <Label>인식된 텍스트:</Label>
                    <div className="font-medium">{voiceResult.text}</div>
                  </div>
                  <div>
                    <Label>명령 타입:</Label>
                    <Badge>{voiceResult.command_type}</Badge>
                  </div>
                  <div>
                    <Label>응답:</Label>
                    <div className="font-medium">{voiceResult.response}</div>
                  </div>
                  <div>
                    <Label>신뢰도:</Label>
                    <div className="text-sm">{(voiceResult.confidence * 100).toFixed(1)}%</div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 이미지 분석 */}
        <TabsContent value="image" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>이미지 분석</CardTitle>
              <CardDescription>
                QR 코드, OCR, 품질 검사를 수행하세요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 이미지 업로드 */}
              <div className="space-y-2">
                <Label>이미지 선택</Label>
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                />
              </div>

              {/* 분석 타입 선택 */}
              <div className="space-y-2">
                <Label>분석 타입</Label>
                <div className="flex flex-wrap gap-2">
                  {['qr_code', 'ocr', 'quality', 'object_detection', 'face_detection'].map((type) => (
                    <Badge
                      key={type}
                      variant={analysisTypes.includes(type) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => {
                        setAnalysisTypes(prev =>
                          prev.includes(type)
                            ? prev.filter(t => t !== type)
                            : [...prev, type]
                        );
                      }}
                    >
                      {type.replace('_', ' ')}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* 분석 버튼 */}
              <Button onClick={analyzeImage} disabled={!selectedImage || loading}>
                <Zap className="h-4 w-4 mr-2" />
                이미지 분석
              </Button>

              {/* 분석 결과 */}
              {imageAnalysis.length > 0 && (
                <div className="space-y-4">
                  <Label>분석 결과</Label>
                  {imageAnalysis.map((analysis, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="font-medium mb-2">
                        {analysis.analysis_type.replace('_', ' ').toUpperCase()}
                      </div>
                      <pre className="text-sm bg-gray-100 p-2 rounded overflow-auto">
                        {JSON.stringify(analysis.results, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 실시간 번역 */}
        <TabsContent value="translation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>실시간 번역</CardTitle>
              <CardDescription>
                텍스트를 다양한 언어로 번역하세요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 번역 입력 */}
              <div className="space-y-2">
                <Label>번역할 텍스트</Label>
                <Textarea
                  value={translateText}
                  onChange={(e) => setTranslateText(e.target.value)}
                  placeholder="번역할 텍스트를 입력하세요..."
                  rows={3}
                />
              </div>

              {/* 대상 언어 선택 */}
              <div className="space-y-2">
                <Label>번역할 언어</Label>
                <Select value={targetLanguage} onValueChange={setTargetLanguage}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(supportedLanguages).map(([code, name]) => (
                      <SelectItem key={code} value={code}>
                        {name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* 번역 버튼 */}
              <Button onClick={handleTranslateText} disabled={!translateText.trim() || loading}>
                <Languages className="h-4 w-4 mr-2" />
                번역하기
              </Button>

              {/* 번역 결과 */}
              {translationResult && (
                <div className="space-y-2 p-4 border rounded-lg">
                  <div>
                    <Label>번역 결과:</Label>
                    <div className="font-medium">{translationResult.translated_text}</div>
                  </div>
                  <div className="flex gap-4 text-sm text-gray-500">
                    <span>신뢰도: {(translationResult.confidence * 100).toFixed(1)}%</span>
                    <span>처리 시간: {translationResult.processing_time.toFixed(2)}초</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedFeatures; 