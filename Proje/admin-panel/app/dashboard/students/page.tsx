'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui';
import { Search, Filter, UserCircle, CheckCircle, XCircle } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface Student {
  id: string;
  full_name: string;
  email: string | null;
  phone_number: string | null;
  room_number: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  dorm_name: string | null;
  created_at: string;
}

const ROLE_LABELS: Record<string, string> = {
  STUDENT: 'Öğrenci',
  DORM_MANAGER: 'Yurt Müdürü',
  SECURITY: 'Güvenlik',
  SYS_ADMIN: 'Sistem Admin',
};

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

export default function StudentsPage() {
  const [users, setUsers] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState<number | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const limit = 20;

  const hasMore = total !== null && users.length < total;

  const fetchUsers = async (pageNum: number, append: boolean) => {
    const params: Record<string, string | number> = {
      page: pageNum,
      limit,
    };
    if (roleFilter !== 'ALL') params.role = roleFilter;
    if (searchQuery.trim()) params.search = searchQuery.trim();

    const res = await apiClient.get('/admin/users', { params });
    const items = res.data.items || [];
    const totalCount = res.data.total ?? 0;
    setTotal(totalCount);
    if (append) {
      setUsers((prev) => {
        const ids = new Set(prev.map((u) => u.id));
        const newItems = items.filter((u: Student) => !ids.has(u.id));
        return [...prev, ...newItems];
      });
    } else {
      setUsers(items);
    }
  };

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const params: Record<string, string | number> = { page: 1, limit };
        if (roleFilter !== 'ALL') params.role = roleFilter;
        if (searchQuery.trim()) params.search = searchQuery.trim();
        const res = await apiClient.get('/admin/users', { params });
        const items = res.data.items || [];
        setUsers(items);
        setTotal(res.data.total ?? items.length);
        setPage(1);
      } catch (err: unknown) {
        const e = err as { response?: { data?: { detail?: string } } };
        setError(e.response?.data?.detail || 'Kullanıcılar yüklenirken hata oluştu');
        setUsers([]);
        setTotal(0);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    run();
    return () => {
      cancelled = true;
    };
  }, [roleFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    apiClient
      .get('/admin/users', {
        params: { page: 1, limit, role: roleFilter !== 'ALL' ? roleFilter : undefined, search: searchQuery.trim() || undefined },
      })
      .then((res) => {
        setUsers(res.data.items || []);
        setTotal(res.data.total ?? 0);
        setPage(1);
      })
      .catch((err: unknown) => {
        const e = err as { response?: { data?: { detail?: string } } };
        setError(e.response?.data?.detail || 'Arama hatası');
        setUsers([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  };

  const handleLoadMore = () => {
    if (!hasMore || loadingMore) return;
    setLoadingMore(true);
    const nextPage = page + 1;
    const params: Record<string, string | number> = { page: nextPage, limit };
    if (roleFilter !== 'ALL') params.role = roleFilter;
    if (searchQuery.trim()) params.search = searchQuery.trim();
    apiClient
      .get('/admin/users', { params })
      .then((res) => {
        const items = res.data.items || [];
        setUsers((prev) => {
          const ids = new Set(prev.map((u) => u.id));
          const newItems = items.filter((u: Student) => !ids.has(u.id));
          return [...prev, ...newItems];
        });
        setTotal(res.data.total ?? 0);
        setPage(nextPage);
      })
      .finally(() => setLoadingMore(false));
  };

  const stats = {
    total: users.length,
    students: users.filter((u) => u.role === 'STUDENT').length,
    verified: users.filter((u) => u.is_verified).length,
    active: users.filter((u) => u.is_active).length,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Öğrenci & Kullanıcı Listesi</h1>
        <p className="text-gray-700 mt-1">
          Kayıtlı öğrenci ve personeli görüntüleyin
        </p>
      </div>

      {loading && users.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-gray-600">Yükleniyor...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4">
              <div className="text-sm text-gray-600">Listelenen</div>
              <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-blue-600">Öğrenci</div>
              <div className="text-2xl font-bold text-blue-700">{stats.students}</div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-green-600">Onaylı</div>
              <div className="text-2xl font-bold text-green-700">{stats.verified}</div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-gray-600">Aktif</div>
              <div className="text-2xl font-bold text-gray-900">{stats.active}</div>
            </Card>
          </div>

          <Card className="p-4">
            <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Ad soyad ile ara..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                >
                  <option value="ALL">Tüm Roller</option>
                  <option value="STUDENT">Öğrenci</option>
                  <option value="DORM_MANAGER">Yurt Müdürü</option>
                  <option value="SECURITY">Güvenlik</option>
                  <option value="SYS_ADMIN">Sistem Admin</option>
                </select>
              </div>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Ara
              </button>
            </form>
          </Card>

          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Ad Soyad</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Telefon</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Oda</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Yurt</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Rol</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Aktif</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Onaylı</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Kayıt</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="px-6 py-16 text-center text-gray-500">
                        <UserCircle className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                        <p className="font-medium">Kullanıcı bulunamadı</p>
                        <p className="text-sm mt-1">Farklı arama veya filtre deneyin.</p>
                      </td>
                    </tr>
                  ) : (
                    users.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">{user.full_name}</td>
                        <td className="px-6 py-4 text-gray-600">{user.email ?? '—'}</td>
                        <td className="px-6 py-4 text-gray-600">{user.phone_number ?? '—'}</td>
                        <td className="px-6 py-4 text-gray-600">{user.room_number ?? '—'}</td>
                        <td className="px-6 py-4 text-gray-600">{user.dorm_name ?? '—'}</td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                            {ROLE_LABELS[user.role] ?? user.role}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {user.is_active ? (
                            <span className="inline-flex items-center gap-1 text-green-700">
                              <CheckCircle className="w-4 h-4" /> Aktif
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-red-600">
                              <XCircle className="w-4 h-4" /> Pasif
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {user.is_verified ? (
                            <span className="text-green-700 font-medium">Evet</span>
                          ) : (
                            <span className="text-gray-500">Hayır</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{formatDate(user.created_at)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            {total !== null && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50">
                <div className="text-sm text-gray-700">
                  Gösterilen: <span className="font-medium">{users.length}</span>
                  {total > 0 && <> / {total}</>}
                </div>
                {hasMore && (
                  <button
                    onClick={handleLoadMore}
                    disabled={loadingMore}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-60 font-medium"
                  >
                    {loadingMore ? 'Yükleniyor...' : 'Daha fazla yükle'}
                  </button>
                )}
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
