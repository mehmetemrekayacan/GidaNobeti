/**
 * Dashboard Page - Statistics & Charts
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui';
import { isAuthenticated } from '@/lib/auth';
import { apiClient } from '@/lib/api-client';
import {
  ShoppingCart,
  Users,
  AlertTriangle,
  ShieldAlert,
  Calendar,
  Activity,
} from 'lucide-react';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface DashboardStats {
  period: string;
  total_orders: number;
  total_students: number;
  total_incidents: number;
  top_restaurants: Array<{ name: string; order_count: number }>;
  incidents_by_restaurant: Array<{ restaurant: string; incident_count: number }>;
  daily_breakdown: Array<{
    date: string;
    orders?: number;
    incidents?: number;
    incident_count?: number;
    total_incidents?: number;
  }>;
}

type ChartPoint = {
  date: string;
  displayDate: string;
  orders: number;
  incidents: number;
};

function formatDate(dateStr: string) {
  const [year, month, day] = dateStr.split('-').map(Number);
  const d = new Date(year, (month || 1) - 1, day || 1);
  return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' });
}

function calcTrend(
  data: Array<{ orders?: number; incidents?: number }>,
  key: 'orders' | 'incidents'
): string {
  if (!data || data.length < 2) return '—';
  const half = Math.floor(data.length / 2);
  const firstHalf = data.slice(0, half).reduce((s, i) => s + (i[key] || 0), 0);
  const secondHalf = data.slice(half).reduce((s, i) => s + (i[key] || 0), 0);
  if (firstHalf === 0) return secondHalf > 0 ? '+100%' : '—';
  const pct = Math.round(((secondHalf - firstHalf) / firstHalf) * 100);
  return pct >= 0 ? `+${pct}%` : `${pct}%`;
}

type Period = 'last_7_days' | 'last_30_days';
const PIE_COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6'];

function toNumber(value: unknown): number {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function toDateKey(value: string): string {
  const normalized = String(value || '').trim();
  if (!normalized) return normalized;

  const directDate = normalized.match(/^(\d{4}-\d{2}-\d{2})$/);
  if (directDate) return directDate[1];

  const prefixedDate = normalized.match(/^(\d{4}-\d{2}-\d{2})[T\s]/);
  if (prefixedDate) return prefixedDate[1];

  const parsed = new Date(normalized);
  if (Number.isNaN(parsed.getTime())) return normalized;

  const y = parsed.getFullYear();
  const m = String(parsed.getMonth() + 1).padStart(2, '0');
  const d = String(parsed.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function dateToLocalKey(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function buildChartData(
  dailyBreakdown: DashboardStats['daily_breakdown'],
  period: Period
): ChartPoint[] {
  const days = period === 'last_30_days' ? 30 : 7;
  const map = new Map<string, { orders: number; incidents: number }>();

  (dailyBreakdown || []).forEach((item) => {
    if (!item?.date) return;
    const key = toDateKey(item.date);
    map.set(key, {
      orders: toNumber(item.orders),
      incidents: toNumber(item.incidents ?? item.incident_count ?? item.total_incidents ?? 0),
    });
  });

  const today = new Date();
  const points: ChartPoint[] = [];
  for (let i = days - 1; i >= 0; i -= 1) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    const key = dateToLocalKey(d);
    const row = map.get(key);
    points.push({
      date: key,
      displayDate: formatDate(key),
      orders: row?.orders ?? 0,
      incidents: row?.incidents ?? 0,
    });
  }

  return points;
}

function DashboardSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="rounded-2xl border border-gray-200 bg-white p-5">
            <div className="h-3 w-24 rounded bg-gray-200 mb-3" />
            <div className="h-8 w-20 rounded bg-gray-200 mb-3" />
            <div className="h-3 w-28 rounded bg-gray-200" />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 rounded-2xl border border-gray-200 bg-white p-6 h-80" />
        <div className="rounded-2xl border border-gray-200 bg-white p-6 h-80" />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const [period, setPeriod] = useState<Period>('last_7_days');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const fetchStats = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get('/admin/dashboard/statistics', {
          params: { period },
        });
        setStats(response.data);
        setError(null);
      } catch (err: unknown) {
        const e = err as { response?: { data?: { detail?: string } } };
        setError(e.response?.data?.detail || 'Veri yüklenirken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [router, period]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-red-600 bg-red-50 px-6 py-4 rounded-lg border border-red-200">
          Hata: {error}
        </div>
      </div>
    );
  }

  if (!stats) return null;

  const riskyRestaurantCount = stats.incidents_by_restaurant?.length || 0;
  const chartData = buildChartData(stats.daily_breakdown || [], period);
  const daily = chartData;
  const incidentsByRestaurant = stats.incidents_by_restaurant || [];

  const ordersTrend = calcTrend(daily, 'orders');
  const incidentsTrend = calcTrend(daily, 'incidents');

  const statsCards = [
    {
      title: 'Toplam Sipariş',
      value: stats.total_orders?.toLocaleString('tr-TR') || '0',
      change: ordersTrend,
      icon: ShoppingCart,
      color: 'text-sky-600',
      bgColor: 'bg-sky-50',
    },
    {
      title: 'Aktif Öğrenci',
      value: stats.total_students?.toLocaleString('tr-TR') || '0',
      change: '—',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Aktif Sağlık Vakası',
      value: stats.total_incidents?.toLocaleString('tr-TR') || '0',
      change: incidentsTrend,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      title: 'Riskli Restoran',
      value: riskyRestaurantCount.toString(),
      change: riskyRestaurantCount > 0 ? `${riskyRestaurantCount} adet` : '—',
      icon: ShieldAlert,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
    },
  ];

  const periodLabel = period === 'last_7_days' ? 'Son 7 gün' : 'Son 30 gün';

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Dashboard</h1>
          <p className="text-gray-700 mt-1">{periodLabel} operasyon özeti</p>
        </div>
        <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2 shadow-sm">
          <Calendar className="w-5 h-5 text-gray-500" />
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value as Period)}
            className="px-2 py-1 border-0 focus:ring-0 bg-transparent text-gray-900"
          >
            <option value="last_7_days">Son 7 gün</option>
            <option value="last_30_days">Son 30 gün</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {statsCards.map((stat) => (
          <Card key={stat.title} className="border border-gray-200 shadow-sm hover:shadow-md transition-shadow rounded-2xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p
                  className={`text-sm mt-1 ${
                    stat.change.startsWith('+')
                      ? 'text-green-600'
                      : stat.change.startsWith('-')
                        ? 'text-red-600'
                        : 'text-gray-500'
                  }`}
                >
                  {stat.change === '—' ? 'Önceki döneme göre' : stat.change}
                </p>
              </div>
              <div className={`${stat.bgColor} p-3 rounded-full`}>
                <stat.icon className={stat.color} size={24} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <Card className="xl:col-span-2 border border-gray-200 shadow-sm rounded-2xl">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-sky-600" />
            <h2 className="text-lg font-semibold text-gray-900">Günlük Sipariş & Vaka Trendi</h2>
          </div>
          <div className="h-64">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="displayDate" tick={{ fontSize: 12, fill: '#374151' }} />
                  <YAxis tick={{ fontSize: 12, fill: '#374151' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', color: '#1f2937' }}
                    labelStyle={{ color: '#1f2937', fontWeight: 600 }}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    formatter={(value: any) => [Number(value ?? 0)]}
                    labelFormatter={(label) => label}
                  />
                  <Line
                    type="monotone"
                    dataKey="orders"
                    name="Sipariş"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="incidents"
                    name="Vaka"
                    stroke="#ef4444"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center bg-gray-50 rounded text-gray-500 text-sm">
                Henüz veri yok
              </div>
            )}
          </div>
        </Card>

        <Card className="border border-gray-200 shadow-sm rounded-2xl">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Riskli Restoran Dağılımı</h2>
          <div className="h-64">
            {incidentsByRestaurant.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={incidentsByRestaurant.map((item) => ({
                      name: item.restaurant,
                      value: item.incident_count,
                    }))}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label={({ name, percent }: { name?: string; percent?: number }) =>
                      `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`
                    }
                  >
                    {incidentsByRestaurant.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    formatter={(value: any) => [Number(value ?? 0), 'Vaka']}
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', color: '#1f2937' }}
                    labelStyle={{ color: '#1f2937', fontWeight: 600 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center bg-gray-50 rounded text-gray-500 text-sm">
                Riskli restoran verisi bulunamadı
              </div>
            )}
          </div>
        </Card>
      </div>

      <Card className="border border-gray-200 shadow-sm rounded-2xl">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">En Çok Sipariş Verilen Restoranlar</h2>
        <div className="space-y-3">
          {stats.top_restaurants.length > 0 ? (
            stats.top_restaurants.map((restaurant, index) => (
              <div
                key={restaurant.name}
                className="flex items-center justify-between rounded-xl border border-gray-100 px-4 py-3 bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-sky-100 text-sky-700 text-sm font-semibold">
                    {index + 1}
                  </span>
                  <span className="font-medium text-gray-800">{restaurant.name}</span>
                </div>
                <span className="text-sm font-semibold text-gray-700">
                  {restaurant.order_count.toLocaleString('tr-TR')} sipariş
                </span>
              </div>
            ))
          ) : (
            <div className="text-sm text-gray-500">Henüz restoran sıralama verisi yok</div>
          )}
        </div>
      </Card>

      <style jsx global>{`
        .fixed.inset-0.bg-black,
        .fixed.inset-0[class*='bg-black'] {
          background-color: rgba(0, 0, 0, 0.5) !important;
          backdrop-filter: blur(4px);
          -webkit-backdrop-filter: blur(4px);
        }
      `}</style>
    </div>
  );
}
