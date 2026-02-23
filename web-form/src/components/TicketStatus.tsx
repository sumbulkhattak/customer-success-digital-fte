'use client';

import { useState, useEffect } from 'react';

interface TicketData {
  ticket_number: string;
  status: string;
  subject: string;
  category: string | null;
  priority: string;
  channel: string;
  created_at: string;
  updated_at: string;
  resolution: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  open: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  resolved: 'bg-green-100 text-green-800',
  escalated: 'bg-orange-100 text-orange-800',
  closed: 'bg-gray-100 text-gray-800',
};

export default function TicketStatus({ ticketId }: { ticketId: string }) {
  const [ticket, setTicket] = useState<TicketData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchStatus = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`/api/support/ticket/${ticketId}`);
      if (!response.ok) {
        throw new Error(response.status === 404 ? 'Ticket not found' : 'Failed to fetch status');
      }
      const data: TicketData = await response.json();
      setTicket(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load ticket status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (ticketId) {
      fetchStatus();
      // Poll every 30 seconds
      const interval = setInterval(fetchStatus, 30000);
      return () => clearInterval(interval);
    }
  }, [ticketId]);

  if (loading && !ticket) {
    return <p className="text-sm text-gray-500 mt-4">Loading ticket status...</p>;
  }

  if (error) {
    return <p className="text-sm text-red-500 mt-4">{error}</p>;
  }

  if (!ticket) return null;

  const statusColor = STATUS_COLORS[ticket.status] || 'bg-gray-100 text-gray-800';

  return (
    <div className="mt-4 border rounded-lg p-4 text-left">
      <h3 className="text-sm font-medium text-gray-700 mb-2">Ticket Status</h3>
      <div className="flex items-center gap-2 mb-2">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}>
          {ticket.status.replace('_', ' ').toUpperCase()}
        </span>
        <span className="text-xs text-gray-500">
          Updated: {new Date(ticket.updated_at).toLocaleString()}
        </span>
      </div>
      {ticket.resolution && (
        <p className="text-sm text-gray-600 mt-2">
          <strong>Resolution:</strong> {ticket.resolution}
        </p>
      )}
    </div>
  );
}
