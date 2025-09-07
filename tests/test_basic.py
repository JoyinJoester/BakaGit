"""
BakaGit 基础测试

测试核心功能是否正常工作。
"""

import unittest
import sys
from pathlib import Path

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bakagit.core.config import ConfigManager
from bakagit.core.utils import is_git_installed, get_git_version, format_file_size
from bakagit.models.repository import Repository, FileStatus
from bakagit.models.commit import Commit, Branch
from datetime import datetime


class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""
    
    def setUp(self):
        """设置测试环境"""
        # 使用临时配置目录
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
    
    def test_default_config(self):
        """测试默认配置"""
        theme = self.config_manager.get('ui.theme')
        self.assertEqual(theme, 'light')
        
        language = self.config_manager.get('ui.language')
        self.assertEqual(language, 'zh_CN')
    
    def test_set_and_get_config(self):
        """测试设置和获取配置"""
        self.config_manager.set('ui.theme', 'dark')
        theme = self.config_manager.get('ui.theme')
        self.assertEqual(theme, 'dark')
    
    def test_recent_repositories(self):
        """测试最近仓库管理"""
        repo_path = "/test/repo"
        self.config_manager.add_recent_repository(repo_path)
        recent_repos = self.config_manager.get_recent_repositories()
        self.assertIn(repo_path, recent_repos)


class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_format_file_size(self):
        """测试文件大小格式化"""
        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1024 * 1024), "1.0 MB")
    
    def test_git_detection(self):
        """测试Git检测"""
        # 这个测试可能会失败如果系统没有安装Git
        git_installed = is_git_installed()
        if git_installed:
            version = get_git_version()
            self.assertIsNotNone(version)
            self.assertTrue(version.replace('.', '').isdigit() or 
                          any(char.isdigit() for char in version))


class TestModels(unittest.TestCase):
    """测试数据模型"""
    
    def test_repository_model(self):
        """测试仓库模型"""
        repo = Repository(
            path="/test/repo",
            name="test-repo",
            current_branch="main",
            untracked_files=["file1.txt"],
            modified_files=["file2.txt"]
        )
        
        self.assertTrue(repo.has_changes)
        self.assertEqual(repo.total_files_changed, 2)
        self.assertIn("新文件", repo.status_text)
        self.assertIn("修改", repo.status_text)
    
    def test_file_status_model(self):
        """测试文件状态模型"""
        file_status = FileStatus(
            path="/test/file.txt",
            status="modified"
        )
        
        self.assertEqual(file_status.display_name, "file.txt")
        self.assertEqual(file_status.status_text, "已修改")
        self.assertEqual(file_status.status_color, "#ff9800")
    
    def test_commit_model(self):
        """测试提交模型"""
        commit = Commit(
            hash="1234567890abcdef",
            message="Test commit\n\nThis is a test commit",
            author_name="Test User",
            author_email="test@example.com",
            date=datetime.now(),
            files_changed=2,
            insertions=10,
            deletions=5
        )
        
        self.assertEqual(commit.short_hash, "12345678")
        self.assertEqual(commit.summary_line, "Test commit")
        self.assertEqual(commit.description, "This is a test commit")
        self.assertIn("2个文件", commit.stats_text)
        self.assertIn("+10", commit.stats_text)
        self.assertIn("-5", commit.stats_text)
    
    def test_branch_model(self):
        """测试分支模型"""
        branch = Branch(
            name="feature-branch",
            commit_hash="abcdef123456",
            is_current=True,
            ahead_count=2,
            behind_count=1
        )
        
        self.assertEqual(branch.display_name, "* feature-branch [↑2/↓1]")
        self.assertEqual(branch.status_text, "当前分支")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_config_to_dict_conversion(self):
        """测试配置的字典转换"""
        repo = Repository(
            path="/test/repo",
            name="test-repo"
        )
        
        # 转换为字典
        repo_dict = repo.to_dict()
        self.assertIsInstance(repo_dict, dict)
        self.assertEqual(repo_dict['path'], "/test/repo")
        
        # 从字典恢复
        restored_repo = Repository.from_dict(repo_dict)
        self.assertEqual(restored_repo.path, repo.path)
        self.assertEqual(restored_repo.name, repo.name)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestModels))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == "__main__":
    print("BakaGit 基础功能测试")
    print("=" * 50)
    
    success = run_tests()
    
    print("=" * 50)
    if success:
        print("✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败！")
        sys.exit(1)
