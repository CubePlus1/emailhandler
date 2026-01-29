import React, { useState, useEffect, Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline';
import { Email } from '../types/email';

interface ComposeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSend: (data: { to: string; subject: string; body: string }) => void;
  replyTo?: Email;
}

interface FormData {
  to: string;
  subject: string;
  body: string;
}

interface FormErrors {
  to?: string;
  subject?: string;
  body?: string;
}

const ComposeModal: React.FC<ComposeModalProps> = ({
  isOpen,
  onClose,
  onSend,
  replyTo
}) => {
  const [formData, setFormData] = useState<FormData>({
    to: '',
    subject: '',
    body: ''
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [touched, setTouched] = useState<{ [key: string]: boolean }>({});

  // Auto-fill when replying
  useEffect(() => {
    if (replyTo && isOpen) {
      setFormData({
        to: replyTo.from_address,
        subject: replyTo.subject.startsWith('Re: ')
          ? replyTo.subject
          : `Re: ${replyTo.subject}`,
        body: ''
      });
      setTouched({});
      setErrors({});
    } else if (isOpen) {
      setFormData({ to: '', subject: '', body: '' });
      setTouched({});
      setErrors({});
    }
  }, [replyTo, isOpen]);

  // Email validation
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // Validate single field
  const validateField = (name: keyof FormData, value: string): string | undefined => {
    switch (name) {
      case 'to':
        if (!value.trim()) return 'Recipient email is required';
        if (!validateEmail(value.trim())) return 'Invalid email format';
        return undefined;
      case 'subject':
        if (!value.trim()) return 'Subject is required';
        return undefined;
      case 'body':
        if (!value.trim()) return 'Message body is required';
        return undefined;
      default:
        return undefined;
    }
  };

  // Validate all fields
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    (Object.keys(formData) as Array<keyof FormData>).forEach(key => {
      const error = validateField(key, formData[key]);
      if (error) newErrors[key] = error;
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle input change
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear error on change if field was touched
    if (touched[name]) {
      const error = validateField(name as keyof FormData, value);
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  };

  // Handle blur
  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));

    const error = validateField(name as keyof FormData, value);
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  // Handle submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({ to: true, subject: true, body: true });

    if (!validateForm()) return;

    setIsSubmitting(true);

    try {
      await onSend({
        to: formData.to.trim(),
        subject: formData.subject.trim(),
        body: formData.body.trim()
      });

      // Reset form on success
      setFormData({ to: '', subject: '', body: '' });
      setTouched({});
      setErrors({});
      onClose();
    } catch (error) {
      console.error('Failed to send email:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    if (!isSubmitting) {
      setFormData({ to: '', subject: '', body: '' });
      setTouched({});
      setErrors({});
      onClose();
    }
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={handleCancel}>
        {/* Backdrop with gradient blur */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-neutral-900/60 backdrop-blur-sm" />
        </Transition.Child>

        {/* Modal container */}
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95 translate-y-4"
              enterTo="opacity-100 scale-100 translate-y-0"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100 translate-y-0"
              leaveTo="opacity-0 scale-95 translate-y-4"
            >
              <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden transition-all">
                {/* Decorative gradient background */}
                <div className="relative">
                  <div className="absolute -inset-1 bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-500 rounded-2xl blur opacity-20" />

                  <div className="relative bg-white rounded-2xl shadow-2xl border border-neutral-200">
                    {/* Header */}
                    <div className="relative px-8 py-6 border-b border-neutral-200 bg-gradient-to-br from-neutral-50 to-white">
                      <div className="flex items-center justify-between">
                        <Dialog.Title className="text-2xl font-light tracking-tight text-neutral-900">
                          {replyTo ? 'Reply to Email' : 'Compose Email'}
                        </Dialog.Title>

                        <button
                          type="button"
                          onClick={handleCancel}
                          disabled={isSubmitting}
                          className="group p-2 rounded-lg hover:bg-neutral-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <XMarkIcon className="w-5 h-5 text-neutral-500 group-hover:text-neutral-900 transition-colors" />
                        </button>
                      </div>

                      {/* Decorative accent line */}
                      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-50" />
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="p-8 space-y-6">
                      {/* To field */}
                      <div className="space-y-2">
                        <label htmlFor="to" className="block text-sm font-medium text-neutral-700">
                          To <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="email"
                          id="to"
                          name="to"
                          value={formData.to}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          disabled={isSubmitting}
                          placeholder="recipient@example.com"
                          className={`
                            w-full px-4 py-3 rounded-lg border transition-all duration-200
                            bg-neutral-50 focus:bg-white
                            font-mono text-sm
                            disabled:opacity-50 disabled:cursor-not-allowed
                            ${touched.to && errors.to
                              ? 'border-red-300 focus:border-red-500 focus:ring-4 focus:ring-red-100'
                              : 'border-neutral-300 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100'
                            }
                          `}
                        />
                        {touched.to && errors.to && (
                          <p className="text-sm text-red-600 flex items-center gap-1.5">
                            <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
                            {errors.to}
                          </p>
                        )}
                      </div>

                      {/* Subject field */}
                      <div className="space-y-2">
                        <label htmlFor="subject" className="block text-sm font-medium text-neutral-700">
                          Subject <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          id="subject"
                          name="subject"
                          value={formData.subject}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          disabled={isSubmitting}
                          placeholder="Enter subject"
                          className={`
                            w-full px-4 py-3 rounded-lg border transition-all duration-200
                            bg-neutral-50 focus:bg-white
                            disabled:opacity-50 disabled:cursor-not-allowed
                            ${touched.subject && errors.subject
                              ? 'border-red-300 focus:border-red-500 focus:ring-4 focus:ring-red-100'
                              : 'border-neutral-300 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100'
                            }
                          `}
                        />
                        {touched.subject && errors.subject && (
                          <p className="text-sm text-red-600 flex items-center gap-1.5">
                            <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
                            {errors.subject}
                          </p>
                        )}
                      </div>

                      {/* Body field */}
                      <div className="space-y-2">
                        <label htmlFor="body" className="block text-sm font-medium text-neutral-700">
                          Message <span className="text-red-500">*</span>
                        </label>
                        <textarea
                          id="body"
                          name="body"
                          value={formData.body}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          disabled={isSubmitting}
                          placeholder="Write your message..."
                          rows={12}
                          className={`
                            w-full px-4 py-3 rounded-lg border transition-all duration-200
                            bg-neutral-50 focus:bg-white
                            resize-y min-h-[200px]
                            disabled:opacity-50 disabled:cursor-not-allowed
                            ${touched.body && errors.body
                              ? 'border-red-300 focus:border-red-500 focus:ring-4 focus:ring-red-100'
                              : 'border-neutral-300 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100'
                            }
                          `}
                        />
                        {touched.body && errors.body && (
                          <p className="text-sm text-red-600 flex items-center gap-1.5">
                            <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
                            {errors.body}
                          </p>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center justify-end gap-3 pt-4">
                        <button
                          type="button"
                          onClick={handleCancel}
                          disabled={isSubmitting}
                          className="px-6 py-3 rounded-lg border border-neutral-300 text-neutral-700 hover:bg-neutral-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                        >
                          Cancel
                        </button>

                        <button
                          type="submit"
                          disabled={isSubmitting}
                          className="group relative px-6 py-3 rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 text-white font-medium shadow-lg shadow-indigo-200 hover:shadow-xl hover:shadow-indigo-300 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none overflow-hidden"
                        >
                          {/* Shine effect */}
                          <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                          </div>

                          <span className="relative flex items-center gap-2">
                            {isSubmitting ? (
                              <>
                                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                </svg>
                                Sending...
                              </>
                            ) : (
                              <>
                                <PaperAirplaneIcon className="w-5 h-5" />
                                Send Email
                              </>
                            )}
                          </span>
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default ComposeModal;
