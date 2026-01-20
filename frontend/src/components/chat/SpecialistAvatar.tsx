import { SPECIALIST_INFO, type SpecialistRole } from '@/types';

interface SpecialistAvatarProps {
  role: SpecialistRole | 'user';
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'w-6 h-6 text-xs',
  md: 'w-8 h-8 text-sm',
  lg: 'w-10 h-10 text-base',
};

const colorClasses: Record<string, string> = {
  purple: 'bg-purple-100 text-purple-700 border-purple-300',
  blue: 'bg-blue-100 text-blue-700 border-blue-300',
  amber: 'bg-amber-100 text-amber-700 border-amber-300',
  green: 'bg-green-100 text-green-700 border-green-300',
  red: 'bg-red-100 text-red-700 border-red-300',
  gray: 'bg-gray-100 text-gray-700 border-gray-300',
};

export function SpecialistAvatar({ role, size = 'md' }: SpecialistAvatarProps) {
  if (role === 'user') {
    return (
      <div
        className={`${sizeClasses[size]} ${colorClasses.gray} rounded-full border flex items-center justify-center font-medium`}
      >
        U
      </div>
    );
  }

  const info = SPECIALIST_INFO[role];
  if (!info) return null;

  return (
    <div
      className={`${sizeClasses[size]} ${colorClasses[info.color]} rounded-full border flex items-center justify-center`}
      title={info.name}
    >
      {info.icon}
    </div>
  );
}
