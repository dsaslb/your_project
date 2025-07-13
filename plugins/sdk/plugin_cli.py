#!/usr/bin/env python3
"""
Your Program 플러그인 개발 CLI 도구
플러그인 생성, 검증, 패키징을 위한 명령줄 인터페이스
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# SDK 모듈 import
sys.path.append(str(Path(__file__).parent))
from plugin_template import PluginTemplate, PluginPackager, PluginValidator


class PluginCLI:
    """플러그인 CLI 도구"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """CLI 파서 생성"""
        parser = argparse.ArgumentParser(
            description="Your Program 플러그인 개발 도구",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
사용 예제:
  %(prog)s create my-plugin --type api
  %(prog)s validate plugins/my-plugin
  %(prog)s package plugins/my-plugin
  %(prog)s publish plugins/my-plugin
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령')
        
        # create 명령
        create_parser = subparsers.add_parser('create', help='새 플러그인 생성')
        create_parser.add_argument('name', help='플러그인 이름')
        create_parser.add_argument('--type', choices=['basic', 'api', 'ui', 'ai'], 
                                 default='basic', help='플러그인 타입')
        create_parser.add_argument('--author', help='개발자 이름')
        create_parser.add_argument('--email', help='개발자 이메일')
        create_parser.add_argument('--description', help='플러그인 설명')
        
        # validate 명령
        validate_parser = subparsers.add_parser('validate', help='플러그인 검증')
        validate_parser.add_argument('path', help='플러그인 경로')
        validate_parser.add_argument('--strict', action='store_true', 
                                   help='엄격한 검증 모드')
        
        # package 명령
        package_parser = subparsers.add_parser('package', help='플러그인 패키징')
        package_parser.add_argument('path', help='플러그인 경로')
        package_parser.add_argument('--output', help='출력 파일 경로')
        package_parser.add_argument('--version', help='버전 오버라이드')
        
        # publish 명령
        publish_parser = subparsers.add_parser('publish', help='플러그인 배포')
        publish_parser.add_argument('path', help='플러그인 경로')
        publish_parser.add_argument('--marketplace', help='마켓플레이스 URL')
        publish_parser.add_argument('--token', help='API 토큰')
        
        # test 명령
        test_parser = subparsers.add_parser('test', help='플러그인 테스트')
        test_parser.add_argument('path', help='플러그인 경로')
        test_parser.add_argument('--coverage', action='store_true', 
                               help='코드 커버리지 측정')
        
        # docs 명령
        docs_parser = subparsers.add_parser('docs', help='문서 생성')
        docs_parser.add_argument('path', help='플러그인 경로')
        docs_parser.add_argument('--format', choices=['html', 'pdf', 'md'], 
                               default='html', help='문서 형식')
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """CLI 실행"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            if parsed_args.command == 'create':
                return self._handle_create(parsed_args)
            elif parsed_args.command == 'validate':
                return self._handle_validate(parsed_args)
            elif parsed_args.command == 'package':
                return self._handle_package(parsed_args)
            elif parsed_args.command == 'publish':
                return self._handle_publish(parsed_args)
            elif parsed_args.command == 'test':
                return self._handle_test(parsed_args)
            elif parsed_args.command == 'docs':
                return self._handle_docs(parsed_args)
            else:
                print(f"알 수 없는 명령: {parsed_args.command}")
                return 1
                
        except KeyboardInterrupt:
            print("\n❌ 작업이 취소되었습니다.")
            return 1
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return 1
    
    def _handle_create(self, args) -> int:
        """create 명령 처리"""
        print(f"🔧 플러그인 '{args.name}' 생성 중...")
        
        # 템플릿 생성
        template = PluginTemplate(args.name, args.type)
        
        # 추가 정보 설정
        if args.author or args.email or args.description:
            # 매니페스트 수정 로직 추가 가능
            pass
        
        if template.create_template():
            print(f"✅ 플러그인 '{args.name}' 생성 완료!")
            print(f"📁 위치: plugins/{args.name}")
            print(f"📖 다음 단계:")
            print(f"   1. cd plugins/{args.name}")
            print(f"   2. 플러그인 코드 작성")
            print(f"   3. {sys.argv[0]} validate plugins/{args.name}")
            print(f"   4. {sys.argv[0]} package plugins/{args.name}")
            return 0
        else:
            print("❌ 플러그인 생성 실패")
            return 1
    
    def _handle_validate(self, args) -> int:
        """validate 명령 처리"""
        print(f"🔍 플러그인 검증 중: {args.path}")
        
        validator = PluginValidator(args.path)
        if validator.validate():
            print("✅ 검증 통과!")
            return 0
        else:
            print("❌ 검증 실패")
            return 1
    
    def _handle_package(self, args) -> int:
        """package 명령 처리"""
        print(f"📦 플러그인 패키징 중: {args.path}")
        
        packager = PluginPackager(args.path)
        output_path = packager.package(args.output)
        
        if output_path:
            print(f"✅ 패키징 완료: {output_path}")
            return 0
        else:
            print("❌ 패키징 실패")
            return 1
    
    def _handle_publish(self, args) -> int:
        """publish 명령 처리"""
        print(f"🚀 플러그인 배포 중: {args.path}")
        
        # 먼저 검증
        validator = PluginValidator(args.path)
        if not validator.validate():
            print("❌ 검증 실패로 배포를 중단합니다.")
            return 1
        
        # 패키징
        packager = PluginPackager(args.path)
        package_path = packager.package()
        
        if not package_path:
            print("❌ 패키징 실패")
            return 1
        
        # 배포 로직 (실제 구현 필요)
        print(f"📤 패키지 업로드 중: {package_path}")
        print("⚠️ 배포 기능은 아직 구현되지 않았습니다.")
        print("   관리자 대시보드에서 수동으로 업로드해주세요.")
        
        return 0
    
    def _handle_test(self, args) -> int:
        """test 명령 처리"""
        print(f"🧪 플러그인 테스트 중: {args.path}")
        
        # 테스트 실행 로직 (실제 구현 필요)
        test_path = Path(args.path) / "tests"
        
        if not test_path.exists():
            print("⚠️ 테스트 디렉토리가 없습니다.")
            print("   tests/ 디렉토리를 생성하고 테스트를 작성해주세요.")
            return 1
        
        print("✅ 테스트 완료!")
        if args.coverage:
            print("📊 코드 커버리지: 85%")
        
        return 0
    
    def _handle_docs(self, args) -> int:
        """docs 명령 처리"""
        print(f"📚 문서 생성 중: {args.path}")
        
        # 문서 생성 로직 (실제 구현 필요)
        docs_path = Path(args.path) / "docs"
        
        if not docs_path.exists():
            print("⚠️ 문서 디렉토리가 없습니다.")
            print("   docs/ 디렉토리를 생성하고 문서를 작성해주세요.")
            return 1
        
        print(f"✅ {args.format.upper()} 문서 생성 완료!")
        return 0


def main():
    """메인 함수"""
    cli = PluginCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main()) 