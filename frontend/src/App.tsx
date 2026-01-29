import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import EmailList from './components/EmailList';
import EmailView from './components/EmailView';
import ComposeModal from './components/ComposeModal';
import api from './api/client';
import { Email } from './types/email';

function App() {
  const [currentFolder, setCurrentFolder] = useState<string>('inbox');
  const [emails, setEmails] = useState<Email[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // 加载邮件列表
  const loadEmails = async (folder: string = currentFolder) => {
    setIsLoading(true);
    try {
      const response = await api.getEmails(folder, 1);
      setEmails(response.items);
    } catch (error) {
      console.error('加载邮件失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 文件夹切换
  const handleFolderChange = (folder: string) => {
    setCurrentFolder(folder);
    setSelectedEmail(null);
    loadEmails(folder);
  };

  // 邮件选择
  const handleEmailClick = (email: Email) => {
    setSelectedEmail(email);
    // 标记为已读
    if (!email.is_read) {
      api.updateEmail(email.id, { is_read: true })
        .then(() => loadEmails())
        .catch(console.error);
    }
  };

  // 回复邮件
  const handleReply = (email: Email) => {
    setSelectedEmail(email);
    setIsComposeOpen(true);
  };

  // 删除邮件
  const handleDelete = async (email: Email) => {
    if (window.confirm('确定要删除这封邮件吗？')) {
      try {
        await api.deleteEmail(email.id);
        setSelectedEmail(null);
        loadEmails();
      } catch (error) {
        console.error('删除邮件失败:', error);
      }
    }
  };

  // 标星/取消标星
  const handleToggleStar = async (email: Email) => {
    try {
      await api.updateEmail(email.id, { is_starred: !email.is_starred });
      loadEmails();
    } catch (error) {
      console.error('更新邮件失败:', error);
    }
  };

  // 发送邮件
  const handleSend = async (data: { to: string; subject: string; body: string }) => {
    try {
      // TODO: 实现发送邮件 API
      console.log('发送邮件:', data);
      alert('邮件发送功能待实现（P2 优先级）');
      setIsComposeOpen(false);
    } catch (error) {
      console.error('发送邮件失败:', error);
    }
  };

  // 初始加载
  useEffect(() => {
    loadEmails();
  }, []);

  return (
    <Layout
      currentFolder={currentFolder}
      onFolderChange={handleFolderChange}
    >
      <div className="flex h-screen">
        {/* 邮件列表 */}
        <div className="w-1/3 border-r border-gray-200 overflow-y-auto">
          <EmailList
            emails={emails}
            selectedEmailId={selectedEmail?.id}
            onEmailClick={handleEmailClick}
            isLoading={isLoading}
          />
        </div>

        {/* 邮件详情 */}
        <div className="flex-1 overflow-y-auto">
          <EmailView
            email={selectedEmail}
            onClose={() => setSelectedEmail(null)}
            onReply={handleReply}
            onDelete={handleDelete}
            onToggleStar={handleToggleStar}
          />
        </div>
      </div>

      {/* 撰写邮件弹窗 */}
      <ComposeModal
        isOpen={isComposeOpen}
        onClose={() => setIsComposeOpen(false)}
        onSend={handleSend}
        replyTo={selectedEmail || undefined}
      />

      {/* 新建邮件按钮 */}
      <button
        onClick={() => setIsComposeOpen(true)}
        className="fixed bottom-8 right-8 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all hover:scale-110"
        aria-label="撰写邮件"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </Layout>
  );
}

export default App;
