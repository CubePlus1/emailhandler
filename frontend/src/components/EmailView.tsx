import React from 'react';
import DOMPurify from 'dompurify';
import {
  ArrowUturnLeftIcon,
  TrashIcon,
  StarIcon,
  XMarkIcon,
  PaperClipIcon,
  CalendarIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';
import { Email } from '../types/email';

interface EmailViewProps {
  email: Email | null;
  onClose?: () => void;
  onReply?: (email: Email) => void;
  onDelete?: (email: Email) => void;
  onToggleStar?: (email: Email) => void;
}

const EmailView: React.FC<EmailViewProps> = ({
  email,
  onClose,
  onReply,
  onDelete,
  onToggleStar,
}) => {
  if (!email) {
    return (
      <div className="flex items-center justify-center h-full bg-gradient-to-br from-zinc-950 via-neutral-900 to-stone-950">
        <div className="text-center space-y-6 px-8">
          <div className="relative">
            <div className="absolute inset-0 blur-3xl opacity-20 bg-gradient-to-r from-amber-500 via-orange-500 to-red-500" />
            <EnvelopeIcon className="w-32 h-32 text-amber-500/20 mx-auto relative" strokeWidth={0.5} />
          </div>
          <div className="space-y-2">
            <h3 className="text-3xl font-light tracking-tight text-zinc-100">
              No Message Selected
            </h3>
            <p className="text-zinc-500 text-sm font-mono tracking-wider uppercase">
              Choose an email to view its contents
            </p>
          </div>
        </div>
      </div>
    );
  }

  const formatDateTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const sanitizeHTML = (html: string): string => {
    return DOMPurify.sanitize(html, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre', 'code', 'div', 'span', 'img'],
      ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'style'],
    });
  };

  const extractAttachments = (): string[] => {
    // Placeholder for future attachment extraction logic
    return [];
  };

  const attachments = extractAttachments();

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-zinc-950 via-neutral-900 to-stone-950 overflow-hidden">
      {/* Header with Actions */}
      <div className="relative border-b border-amber-500/10 bg-black/40 backdrop-blur-xl">
        <div className="absolute inset-0 bg-gradient-to-r from-amber-500/5 via-transparent to-orange-500/5" />

        <div className="relative px-8 py-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => onReply?.(email)}
              className="group flex items-center gap-2 px-5 py-2.5 bg-amber-500/10 hover:bg-amber-500/20
                       border border-amber-500/30 hover:border-amber-500/50 rounded-none
                       transition-all duration-300 hover:shadow-lg hover:shadow-amber-500/20"
              title="Reply"
            >
              <ArrowUturnLeftIcon className="w-5 h-5 text-amber-400 group-hover:text-amber-300 transition-colors" />
              <span className="text-sm font-mono tracking-wider text-amber-100 uppercase">Reply</span>
            </button>

            <button
              onClick={() => onToggleStar?.(email)}
              className="group p-2.5 bg-zinc-900/50 hover:bg-amber-500/10
                       border border-zinc-800 hover:border-amber-500/30 rounded-none
                       transition-all duration-300"
              title="Toggle Star"
            >
              {email.is_read ? (
                <StarIconSolid className="w-5 h-5 text-amber-400 group-hover:scale-110 transition-transform" />
              ) : (
                <StarIcon className="w-5 h-5 text-zinc-600 group-hover:text-amber-400 transition-colors" />
              )}
            </button>

            <button
              onClick={() => onDelete?.(email)}
              className="group p-2.5 bg-zinc-900/50 hover:bg-red-500/10
                       border border-zinc-800 hover:border-red-500/30 rounded-none
                       transition-all duration-300"
              title="Delete"
            >
              <TrashIcon className="w-5 h-5 text-zinc-600 group-hover:text-red-400 transition-colors" />
            </button>
          </div>

          {onClose && (
            <button
              onClick={onClose}
              className="group p-2.5 bg-zinc-900/50 hover:bg-zinc-800/50
                       border border-zinc-800 hover:border-zinc-700 rounded-none
                       transition-all duration-300"
              title="Close"
            >
              <XMarkIcon className="w-5 h-5 text-zinc-500 group-hover:text-zinc-300 transition-colors" />
            </button>
          )}
        </div>
      </div>

      {/* Email Content */}
      <div className="flex-1 overflow-y-auto px-8 py-8 space-y-8">
        {/* Subject */}
        <div className="space-y-3">
          <div className="h-px bg-gradient-to-r from-transparent via-amber-500/30 to-transparent" />
          <h1 className="text-4xl font-light tracking-tight text-zinc-100 leading-tight">
            {email.subject}
          </h1>
          <div className="h-px bg-gradient-to-r from-transparent via-amber-500/30 to-transparent" />
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* From */}
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative p-6 border border-zinc-800/50 bg-black/20 backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-amber-500/10 border border-amber-500/20">
                  <EnvelopeIcon className="w-5 h-5 text-amber-400" />
                </div>
                <div className="flex-1 space-y-1">
                  <p className="text-xs font-mono tracking-widest text-zinc-600 uppercase">From</p>
                  <p className="text-base text-zinc-200 font-light break-all">{email.from_address}</p>
                </div>
              </div>
            </div>
          </div>

          {/* To */}
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative p-6 border border-zinc-800/50 bg-black/20 backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-orange-500/10 border border-orange-500/20">
                  <EnvelopeIcon className="w-5 h-5 text-orange-400" />
                </div>
                <div className="flex-1 space-y-1">
                  <p className="text-xs font-mono tracking-widest text-zinc-600 uppercase">To</p>
                  <p className="text-base text-zinc-200 font-light break-all">{email.to_address}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Date */}
          <div className="group relative md:col-span-2">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative p-6 border border-zinc-800/50 bg-black/20 backdrop-blur-sm">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-amber-500/10 border border-amber-500/20">
                  <CalendarIcon className="w-5 h-5 text-amber-400" />
                </div>
                <div className="flex-1 space-y-1">
                  <p className="text-xs font-mono tracking-widest text-zinc-600 uppercase">Received</p>
                  <p className="text-base text-zinc-200 font-light">{formatDateTime(email.received_at)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Attachments */}
        {attachments.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <PaperClipIcon className="w-5 h-5 text-amber-500" />
              <h2 className="text-sm font-mono tracking-widest text-zinc-400 uppercase">
                Attachments ({attachments.length})
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {attachments.map((attachment, index) => (
                <div
                  key={index}
                  className="p-4 bg-zinc-900/30 border border-zinc-800/50 hover:border-amber-500/30
                           transition-colors duration-300 cursor-pointer"
                >
                  <p className="text-sm text-zinc-300 font-mono truncate">{attachment}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Email Body */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="h-px flex-1 bg-gradient-to-r from-amber-500/30 to-transparent" />
            <h2 className="text-sm font-mono tracking-widest text-zinc-400 uppercase">Message</h2>
            <div className="h-px flex-1 bg-gradient-to-l from-amber-500/30 to-transparent" />
          </div>

          <div className="relative group">
            <div className="absolute -inset-4 bg-gradient-to-br from-amber-500/5 via-transparent to-orange-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
            <div className="relative p-8 border border-zinc-800/50 bg-black/20 backdrop-blur-sm">
              {email.html_body ? (
                <div
                  className="prose prose-invert prose-amber max-w-none
                           prose-headings:font-light prose-headings:tracking-tight
                           prose-p:text-zinc-300 prose-p:leading-relaxed
                           prose-a:text-amber-400 prose-a:no-underline hover:prose-a:text-amber-300
                           prose-strong:text-zinc-100 prose-strong:font-medium
                           prose-code:text-amber-400 prose-code:bg-black/40 prose-code:px-2 prose-code:py-1
                           prose-pre:bg-black/60 prose-pre:border prose-pre:border-zinc-800
                           prose-blockquote:border-l-4 prose-blockquote:border-amber-500/30 prose-blockquote:text-zinc-400"
                  dangerouslySetInnerHTML={{ __html: sanitizeHTML(email.html_body) }}
                />
              ) : (
                <div className="whitespace-pre-wrap text-zinc-300 leading-relaxed font-light">
                  {email.text_body}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailView;
