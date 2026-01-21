/**
 * Dashboard Layout - Sidebar + Header
 */
'use client';

import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { removeToken } from '@/lib/auth';
import { LayoutDashboard, Users, UtensilsCrossed, AlertTriangle, LogOut, LucideIcon } from 'lucide-react';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();

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
          {menuItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-md transition-colors mb-1 ${
                  isActive 
                    ? 'bg-blue-50 text-blue-600 font-medium' 
                    : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                }`}
              >
                <item.icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
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

// NavLink Component with active state
function NavLink({ href, icon: Icon, children }: { href: string; icon: LucideIcon; children: React.ReactNode }) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link
      href={href}
      className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
        isActive
          ? 'bg-blue-50 text-blue-700 font-medium'
          : 'text-gray-700 hover:bg-gray-100'
      }`}
    >
      <Icon className="w-5 h-5" />
      {children}
    </Link>
  );
}
