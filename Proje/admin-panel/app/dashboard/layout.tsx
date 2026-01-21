/**
 * Dashboard Layout - Sidebar + Header
 */
'use client';

import { useRouter } from 'next/navigation';
import { removeToken } from '@/lib/auth';
import { LayoutDashboard, Users, UtensilsCrossed, AlertTriangle, LogOut } from 'lucide-react';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();

  const handleLogout = () => {
    removeToken();
    router.push('/login');
  };

  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
    { icon: UtensilsCrossed, label: 'Restoranlar', href: '/dashboard/restaurants' },
    { icon: Users, label: 'Siparişler', href: '/dashboard/orders' },
    { icon: AlertTriangle, label: 'Vakalar', href: '/dashboard/incidents' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md flex flex-col" suppressHydrationWarning>
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold text-gray-900">Gıda Nöbeti</h1>
          <p className="text-sm text-gray-600">Yönetici Paneli</p>
        </div>

        <nav className="flex-1 p-4">
          {menuItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors mb-1"
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </a>
          ))}
        </nav>

        <div className="p-4 border-t">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-md transition-colors w-full"
          >
            <LogOut size={20} />
            <span>Çıkış Yap</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
