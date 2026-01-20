'use client';

import { SPECIALIST_INFO, type SpecialistRole } from '@/types';

interface ModelSelectorProps {
  role: SpecialistRole;
  value: string;
  onChange: (value: string) => void;
  availableModels: string[];
}

export function ModelSelector({ role, value, onChange, availableModels }: ModelSelectorProps) {
  const info = SPECIALIST_INFO[role];

  return (
    <div className="flex items-center gap-4 p-4 border rounded-lg">
      <div className="text-2xl">{info.icon}</div>
      <div className="flex-1">
        <div className="font-medium">{info.name}</div>
        <div className="text-sm text-gray-500 capitalize">{role} Specialist</div>
      </div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="border rounded-lg px-3 py-2"
      >
        {availableModels.map((model) => (
          <option key={model} value={model}>
            {model}
          </option>
        ))}
      </select>
    </div>
  );
}
