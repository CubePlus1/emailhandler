import React from 'react';
import { Email, EmailListProps } from '../types/email';
import { formatRelativeTime, truncateText } from '../utils/dateUtils';
import { EnvelopeIcon } from '@heroicons/react/24/outline';

const EmailList: React.FC<EmailListProps> = ({
  emails,
  selectedEmailId,
  onEmailClick,
  isLoading = false
}) => {
  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (!emails || emails.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="flex flex-col h-full bg-neutral-50">
      {/* Header with subtle gradient */}
      <div className="sticky top-0 z-10 backdrop-blur-xl bg-white/80 border-b border-neutral-200 px-8 py-6">
        <div className="flex items-baseline gap-4">
          <h2 className="text-2xl font-light tracking-tight text-neutral-900">Inbox</h2>
          <span className="text-sm font-mono text-neutral-500 tabular-nums">{emails.length}</span>
        </div>
      </div>

      {/* Email list with custom spacing */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-1">
        {emails.map((email) => (
          <EmailListItem
            key={email.id}
            email={email}
            isSelected={email.id === selectedEmailId}
            onClick={() => onEmailClick?.(email)}
          />
        ))}
      </div>
    </div>
  );
};

interface EmailListItemProps {
  email: Email;
  isSelected: boolean;
  onClick: () => void;
}

const EmailListItem: React.FC<EmailListItemProps> = ({ email, isSelected, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`
        group w-full text-left transition-all duration-200 ease-out
        rounded-lg px-6 py-5 relative overflow-hidden
        ${isSelected
          ? 'bg-indigo-600 shadow-lg shadow-indigo-200 scale-[1.01]'
          : 'bg-white hover:bg-neutral-100 hover:shadow-md hover:-translate-y-0.5'
        }
        ${!email.is_read && !isSelected ? 'ring-2 ring-indigo-200' : ''}
      `}
    >
      {/* Unread indicator - bold accent */}
      {!email.is_read && !isSelected && (
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-indigo-500 to-violet-500" />
      )}

      <div className="flex items-start gap-4">
        {/* Unread dot */}
        <div className="flex-shrink-0 pt-1.5">
          {!email.is_read ? (
            <div className={`w-2.5 h-2.5 rounded-full ${isSelected ? 'bg-white' : 'bg-indigo-500'} animate-pulse`} />
          ) : (
            <div className="w-2.5 h-2.5" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-2">
          {/* From and time */}
          <div className="flex items-baseline justify-between gap-4">
            <span className={`
              text-sm font-medium truncate
              ${isSelected
                ? 'text-white'
                : email.is_read
                  ? 'text-neutral-600'
                  : 'text-neutral-900'
              }
            `}>
              {email.from_address}
            </span>
            <time className={`
              text-xs font-mono tabular-nums flex-shrink-0
              ${isSelected ? 'text-indigo-100' : 'text-neutral-500'}
            `}>
              {formatRelativeTime(email.received_at)}
            </time>
          </div>

          {/* Subject - bold and prominent */}
          <h3 className={`
            text-base leading-snug truncate
            ${isSelected
              ? 'text-white font-semibold'
              : email.is_read
                ? 'text-neutral-700 font-normal'
                : 'text-neutral-900 font-semibold'
            }
          `}>
            {email.subject || '(No Subject)'}
          </h3>

          {/* Preview text */}
          <p className={`
            text-sm leading-relaxed line-clamp-2
            ${isSelected
              ? 'text-indigo-50'
              : email.is_read
                ? 'text-neutral-500'
                : 'text-neutral-600'
            }
          `}>
            {truncateText(email.text_body, 150)}
          </p>
        </div>
      </div>

      {/* Hover indicator - subtle diagonal accent */}
      {!isSelected && (
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
          <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-indigo-100/50 to-transparent transform translate-x-12 -translate-y-12 rotate-12" />
        </div>
      )}
    </button>
  );
};

const LoadingSkeleton: React.FC = () => {
  return (
    <div className="flex flex-col h-full bg-neutral-50">
      <div className="sticky top-0 backdrop-blur-xl bg-white/80 border-b border-neutral-200 px-8 py-6">
        <div className="flex items-baseline gap-4">
          <div className="h-8 w-24 bg-neutral-200 animate-pulse rounded" />
          <div className="h-5 w-8 bg-neutral-200 animate-pulse rounded" />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-1">
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-lg px-6 py-5 space-y-3"
            style={{ animationDelay: `${i * 75}ms` }}
          >
            <div className="flex items-baseline justify-between gap-4">
              <div className="h-5 w-48 bg-neutral-200 animate-pulse rounded" />
              <div className="h-4 w-16 bg-neutral-200 animate-pulse rounded" />
            </div>
            <div className="h-6 w-3/4 bg-neutral-300 animate-pulse rounded" />
            <div className="space-y-2">
              <div className="h-4 w-full bg-neutral-200 animate-pulse rounded" />
              <div className="h-4 w-5/6 bg-neutral-200 animate-pulse rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const EmptyState: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full bg-neutral-50 px-8">
      <div className="relative">
        {/* Decorative gradient circle */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-100 via-violet-100 to-purple-100 rounded-full blur-3xl opacity-60 scale-150" />

        <div className="relative bg-white rounded-2xl p-12 shadow-xl border border-neutral-200">
          <div className="flex flex-col items-center gap-6 text-center max-w-sm">
            {/* Icon with gradient */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-2xl blur-lg opacity-30" />
              <div className="relative bg-gradient-to-br from-indigo-500 to-violet-500 p-6 rounded-2xl">
                <EnvelopeIcon className="w-12 h-12 text-white" strokeWidth={1.5} />
              </div>
            </div>

            {/* Text content */}
            <div className="space-y-2">
              <h3 className="text-2xl font-light text-neutral-900 tracking-tight">
                No messages yet
              </h3>
              <p className="text-sm text-neutral-500 leading-relaxed">
                Your inbox is empty. New emails will appear here when they arrive.
              </p>
            </div>

            {/* Decorative element */}
            <div className="flex gap-2 opacity-40">
              <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailList;
