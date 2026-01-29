import React, { useState } from 'react';
import {
  InboxIcon,
  PaperAirplaneIcon,
  TrashIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

interface LayoutProps {
  children: React.ReactNode;
  currentFolder?: string;
  onFolderChange?: (folder: string) => void;
}

interface FolderItem {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  count?: number;
}

const folders: FolderItem[] = [
  { id: 'inbox', name: 'Inbox', icon: InboxIcon, count: 0 },
  { id: 'sent', name: 'Sent', icon: PaperAirplaneIcon },
  { id: 'trash', name: 'Trash', icon: TrashIcon },
];

export default function Layout({ children, currentFolder = 'inbox', onFolderChange }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleFolderClick = (folderId: string) => {
    onFolderChange?.(folderId);
    setIsSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-64 bg-white shadow-xl z-30 transform transition-transform duration-300 ease-in-out
          lg:translate-x-0
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Sidebar header */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-slate-200 bg-gradient-to-r from-indigo-600 to-blue-600">
          <h1 className="text-xl font-bold text-white tracking-tight">EmailHandler</h1>
          <button
            onClick={() => setIsSidebarOpen(false)}
            className="lg:hidden text-white hover:text-indigo-100 transition-colors"
            aria-label="Close sidebar"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {folders.map((folder) => {
            const Icon = folder.icon;
            const isActive = currentFolder === folder.id;

            return (
              <button
                key={folder.id}
                onClick={() => handleFolderClick(folder.id)}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                  ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-500 to-blue-500 text-white shadow-lg shadow-indigo-200 scale-105'
                      : 'text-slate-700 hover:bg-slate-100 hover:text-indigo-600 hover:translate-x-1'
                  }
                `}
              >
                <Icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                <span className="font-medium flex-1 text-left">{folder.name}</span>
                {folder.count !== undefined && folder.count > 0 && (
                  <span
                    className={`
                      px-2 py-1 text-xs font-semibold rounded-full
                      ${isActive ? 'bg-white text-indigo-600' : 'bg-indigo-100 text-indigo-600'}
                    `}
                  >
                    {folder.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200 bg-slate-50">
          <div className="text-xs text-slate-500 text-center">
            <p className="font-medium">EmailHandler v1.0</p>
            <p className="mt-1">Modern email management</p>
          </div>
        </div>
      </aside>

      {/* Main content area */}
      <div className="lg:ml-64 min-h-screen">
        {/* Top bar */}
        <header className="h-16 bg-white shadow-sm border-b border-slate-200 sticky top-0 z-10">
          <div className="h-full px-4 lg:px-8 flex items-center justify-between">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100 text-slate-600 transition-colors"
              aria-label="Open sidebar"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>

            <div className="flex-1 lg:flex-none">
              <h2 className="text-lg font-semibold text-slate-800 capitalize">
                {folders.find((f) => f.id === currentFolder)?.name || 'Inbox'}
              </h2>
            </div>

            <div className="flex items-center gap-4">
              <div className="hidden sm:block text-sm text-slate-500">
                Welcome to EmailHandler
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
