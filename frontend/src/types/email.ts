export interface Email {
  id: number;
  from_address: string;
  to_address: string;
  subject: string;
  text_body: string;
  html_body?: string;
  received_at: string;
  is_read: boolean;
  created_at: string;
}

export interface EmailListProps {
  emails: Email[];
  selectedEmailId?: number;
  onEmailClick?: (email: Email) => void;
  isLoading?: boolean;
}
