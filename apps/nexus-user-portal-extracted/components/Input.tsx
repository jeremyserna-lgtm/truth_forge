import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  icon,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || props.name || Math.random().toString(36).substr(2, 9);

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label htmlFor={inputId} className="block text-xs font-mono uppercase tracking-wider text-[#888888] mb-2">
          {label}
        </label>
      )}
      <div className="relative group">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-[#4A4A4A] group-focus-within:text-[#F5F0E6] transition-colors">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          className={`
            w-full py-3 bg-[#1A1A1A] border rounded-sm text-[#F5F0E6] placeholder-[#4A4A4A]
            font-sans text-sm transition-colors focus:outline-none focus:ring-1 focus:ring-[#F5F0E6]
            ${icon ? 'pl-11 pr-4' : 'px-4'}
            ${error 
              ? 'border-red-900 focus:border-red-500 focus:ring-red-500' 
              : 'border-[#2D2D2D] focus:border-[#F5F0E6]'}
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
          {...props}
        />
      </div>
      {error && <p className="mt-1 text-xs text-red-400 font-mono">{error}</p>}
      {helperText && !error && <p className="mt-1 text-xs text-[#888888] font-mono">{helperText}</p>}
    </div>
  );
};