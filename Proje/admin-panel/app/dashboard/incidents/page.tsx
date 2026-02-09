'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { Card } from '@/components/ui';
import { Search, Filter, Edit2, AlertTriangle, Clock, CheckCircle, XCircle, X, Stethoscope, Inbox } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

const ADMIN_NOTE_MAX_LENGTH = 2000;

interface Incident {
  id: string;
  user_full_name: string;
  restaurant_name: string | null;
  suspected_order_id?: string | null;
  symptoms: string;
  severity_level: number | null;
  status: string;
  report_date: string;
  admin_notes: string | null;
  is_verified_by_doctor?: boolean;
  updated_at?: string | null;
}

const STATUS_LABELS: Record<string, string> = {
  PENDING: 'Beklemede',
  INVESTIGATING: 'İnceleniyor',
  CONFIRMED: 'Onaylandı',
  DISMISSED: 'Reddedildi',
};

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showToast = useCallback((type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3500);
  }, []);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const params: Record<string, string | number> = { page, limit };
      if (statusFilter !== 'ALL') params.status = statusFilter;
      const response = await apiClient.get('/admin/incidents', { params });
      setIncidents(response.data.items);
      setTotal(response.data.total);
      setError(null);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(axiosError.response?.data?.detail || 'Vakalar yüklenirken hata oluştu');
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [page, statusFilter]);

  const filteredIncidents = incidents.filter((i) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      i.user_full_name.toLowerCase().includes(q) ||
      (i.restaurant_name?.toLowerCase().includes(q) ?? false) ||
      i.symptoms.toLowerCase().includes(q)
    );
  });

  const handleUpdate = async (incidentId: string, status: string, adminNotes: string) => {
    try {
      await apiClient.put(`/admin/incidents/${incidentId}`, {
        status: status || undefined,
        admin_notes: adminNotes || undefined,
      });
      setShowModal(false);
      setSelectedIncident(null);
      fetchIncidents();
      showToast('success', 'Vaka başarıyla güncellendi');
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosError.response?.data?.detail || axiosError.message || 'Güncelleme hatası';
      showToast('error', msg);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      PENDING: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      INVESTIGATING: 'bg-blue-100 text-blue-800 border-blue-200',
      CONFIRMED: 'bg-green-100 text-green-800 border-green-200',
      DISMISSED: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    const icons: Record<string, React.ReactNode> = {
      PENDING: <Clock className="w-4 h-4" />,
      INVESTIGATING: <AlertTriangle className="w-4 h-4" />,
      CONFIRMED: <CheckCircle className="w-4 h-4" />,
      DISMISSED: <XCircle className="w-4 h-4" />,
    };
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${styles[status] || 'bg-gray-100 text-gray-800'}`}
      >
        {icons[status]}
        {STATUS_LABELS[status] || status}
      </span>
    );
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6 relative">
      {/* Toast */}
      {toast && (
        <div
          role="alert"
          aria-live="polite"
          className={`fixed top-4 right-4 z-100 px-4 py-3 rounded-lg shadow-lg text-gray-900 font-medium ${
            toast.type === 'success' ? 'bg-green-100 border border-green-300' : 'bg-red-100 border border-red-300'
          }`}
        >
          {toast.message}
        </div>
      )}

      <div>
        <h1 className="text-2xl font-bold text-gray-900">Sağlık Vakaları</h1>
        <p className="text-gray-700 mt-1">
          Öğrenci şikayetlerini görüntüleyin ve yönetin
        </p>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-gray-600">Vakalar yükleniyor...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          Hata: {error}
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Filters */}
          <Card className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Öğrenci veya restoran ara..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-600"
                  />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    setPage(1);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 [&>option]:text-gray-900"
                >
                  <option value="ALL">Tüm Durumlar</option>
                  <option value="PENDING">Beklemede</option>
                  <option value="INVESTIGATING">İnceleniyor</option>
                  <option value="CONFIRMED">Onaylandı</option>
                  <option value="DISMISSED">Reddedildi</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Table */}
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                      Öğrenci
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                      Restoran
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                      Semptomlar
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                      Şiddet
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                      Durum
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                      Tarih
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                      İşlem
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredIncidents.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-16">
                        <div className="flex flex-col items-center justify-center gap-3 text-gray-500">
                          <Inbox className="w-12 h-12 text-gray-300" />
                          <p className="font-medium text-gray-600">
                            {incidents.length === 0 ? 'Henüz vaka bildirimi yok' : 'Filtreye uygun vaka bulunamadı'}
                          </p>
                          <p className="text-sm">
                            {incidents.length === 0 ? 'Öğrenciler şikayet bildirdiğinde burada görünecek.' : 'Farklı filtreler deneyin.'}
                          </p>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    filteredIncidents.map((incident) => (
                      <tr key={incident.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">
                          {incident.user_full_name}
                        </td>
                        <td className="px-6 py-4 text-gray-800">
                          {incident.restaurant_name || '-'}
                        </td>
                        <td className="px-6 py-4 text-gray-800 max-w-xs truncate">
                          {incident.symptoms}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`font-medium ${
                              incident.severity_level && incident.severity_level >= 4
                                ? 'text-red-600'
                                : 'text-gray-900'
                            }`}
                          >
                            {incident.severity_level ?? '-'}/5
                          </span>
                        </td>
                        <td className="px-6 py-4">{getStatusBadge(incident.status)}</td>
                        <td className="px-6 py-4 text-gray-800 text-sm">
                          {new Date(incident.report_date).toLocaleDateString('tr-TR')}
                        </td>
                        <td className="px-6 py-4">
                          <button
                            onClick={() => {
                              setSelectedIncident(incident);
                              setShowModal(true);
                            }}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                          >
                            <Edit2 className="w-4 h-4" />
                            Düzenle
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t flex justify-between items-center">
                <span className="text-sm text-gray-800">
                  Toplam {total} vaka
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page <= 1}
                    className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 text-gray-900"
                  >
                    Önceki
                  </button>
                  <span className="px-4 py-2 text-gray-800">
                    {page} / {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages}
                    className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 text-gray-900"
                  >
                    Sonraki
                  </button>
                </div>
              </div>
            )}
          </Card>

          {/* Detail/Edit Modal */}
          {showModal && selectedIncident && (
            <IncidentModal
              incident={selectedIncident}
              onClose={() => {
                setShowModal(false);
                setSelectedIncident(null);
              }}
              onSave={handleUpdate}
            />
          )}
        </>
      )}
    </div>
  );
}

function IncidentModal({
  incident,
  onClose,
  onSave,
}: {
  incident: Incident;
  onClose: () => void;
  onSave: (id: string, status: string, adminNotes: string) => void;
}) {
  const [status, setStatus] = useState(incident.status);
  const [adminNotes, setAdminNotes] = useState(incident.admin_notes || '');
  const modalRef = useRef<HTMLDivElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(incident.id, status, adminNotes);
  };

  // Esc ile kapatma
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  // Focus trap - modal açıldığında ilk focusable elemente odaklan
  useEffect(() => {
    const firstFocusable = modalRef.current?.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    firstFocusable?.focus();
  }, []);

  const severity = incident.severity_level ?? 0;
  const severityColor = severity >= 4 ? 'bg-red-500' : severity >= 3 ? 'bg-yellow-500' : 'bg-green-500';

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby="modal-desc"
    >
      <div
        ref={modalRef}
        className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl max-h-[90vh] overflow-y-auto text-gray-900"
        tabIndex={-1}
      >
        {/* Header with X button */}
        <div className="flex items-start justify-between mb-4">
          <h2 id="modal-title" className="text-xl font-bold text-gray-900">Vaka Detayı</h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-gray-500 hover:text-gray-800 hover:bg-gray-100 transition-colors"
            aria-label="Kapat"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div id="modal-desc" className="space-y-3 mb-6 text-sm text-gray-900">
          <p><span className="font-medium text-gray-800">Öğrenci:</span> <span className="text-gray-900">{incident.user_full_name}</span></p>
          <p><span className="font-medium text-gray-800">Restoran:</span> <span className="text-gray-900">{incident.restaurant_name || '-'}</span></p>
          {incident.suspected_order_id && (
            <p>
              <span className="font-medium text-gray-800">Sipariş:</span>{' '}
              <a
                href={`/dashboard/orders?order=${incident.suspected_order_id}`}
                className="text-blue-600 hover:underline"
              >
                {incident.suspected_order_id.slice(0, 8)}...
              </a>
            </p>
          )}
          <p><span className="font-medium text-gray-800">Semptomlar:</span> <span className="text-gray-900">{incident.symptoms}</span></p>
          <p><span className="font-medium text-gray-800">Şiddet:</span>{' '}
            {incident.severity_level != null ? (
              <span className="inline-flex items-center gap-2">
                <span className="flex w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <span
                    className={`h-full ${severityColor} rounded-full transition-all`}
                    style={{ width: `${(incident.severity_level / 5) * 100}%` }}
                  />
                </span>
                <span className="text-gray-900">{incident.severity_level}/5</span>
              </span>
            ) : (
              <span className="text-gray-900">-</span>
            )}
          </p>
          <p><span className="font-medium text-gray-800">Tarih:</span> <span className="text-gray-900">{new Date(incident.report_date).toLocaleString('tr-TR')}</span></p>
          {incident.is_verified_by_doctor && (
            <p>
              <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                <Stethoscope className="w-3.5 h-3.5" />
                Doktor onaylı
              </span>
            </p>
          )}
          {incident.updated_at && (
            <p className="text-gray-600 text-xs">
              Son güncelleme: {new Date(incident.updated_at).toLocaleString('tr-TR')}
            </p>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="incident-status" className="block text-sm font-medium text-gray-800 mb-2">Durum</label>
            <select
              id="incident-status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 [&>option]:text-gray-900 [&>option]:bg-white"
              aria-label="Vaka durumu"
            >
              <option value="PENDING">Beklemede</option>
              <option value="INVESTIGATING">İnceleniyor</option>
              <option value="CONFIRMED">Onaylandı</option>
              <option value="DISMISSED">Reddedildi</option>
            </select>
          </div>

          <div>
            <label htmlFor="incident-notes" className="block text-sm font-medium text-gray-800 mb-2">
              Admin Notu{' '}
              <span className="text-gray-500 font-normal">
                ({adminNotes.length}/{ADMIN_NOTE_MAX_LENGTH})
              </span>
            </label>
            <textarea
              id="incident-notes"
              value={adminNotes}
              onChange={(e) => setAdminNotes(e.target.value.slice(0, ADMIN_NOTE_MAX_LENGTH))}
              maxLength={ADMIN_NOTE_MAX_LENGTH}
              rows={4}
              placeholder="Yönetim notu ekleyin..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-gray-900 placeholder-gray-600"
              aria-describedby="notes-char-count"
            />
            <p id="notes-char-count" className="sr-only">
              {adminNotes.length} karakter kullanıldı, en fazla {ADMIN_NOTE_MAX_LENGTH}
            </p>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-800 rounded-lg hover:bg-gray-50 font-medium transition-colors"
            >
              İptal
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
            >
              Kaydet
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
