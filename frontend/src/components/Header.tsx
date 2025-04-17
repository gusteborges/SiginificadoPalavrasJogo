import React from 'react';

interface HeaderProps {
  onToggleDarkMode: () => void;
  isDarkMode: boolean;
}

export function Header({ onToggleDarkMode, isDarkMode }: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-app-card-light/90 dark:bg-app-card-dark/90 backdrop-blur-sm border-b border-gold-500/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4 flex justify-between items-center">
        <div className="flex-1 flex justify-start">
          <button
            onClick={onToggleDarkMode}
            className="p-2 rounded-full hover:bg-app-background-light/50 dark:hover:bg-app-background-dark/50 transition-colors"
            aria-label={isDarkMode ? 'Ativar modo claro' : 'Ativar modo escuro'}
          >
            {isDarkMode ? (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 sm:h-6 sm:w-6 text-gold-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 sm:h-6 sm:w-6 text-gold-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>
        </div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gold-500 flex-grow text-center font-serif tracking-wide">Ludopália</h1>
        <div className="flex-1"></div>
      </div>
    </header>
  );
}