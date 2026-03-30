import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

export type Locale = 'es' | 'en' | 'de';

export const LOCALES: { code: Locale; label: string }[] = [
  { code: 'es', label: 'Español' },
  { code: 'en', label: 'English' },
  { code: 'de', label: 'Deutsch' },
];

// ── Detectar idioma activo desde la cookie de Google Translate ────────────────
function detectLocale(): Locale {
  if (!browser) return 'es';
  const match = document.cookie.match(/googtrans=\/es\/(\w+)/);
  const lang = match?.[1];
  if (lang === 'en') return 'en';
  if (lang === 'de') return 'de';
  return 'es';
}

export const locale = writable<Locale>(detectLocale());

// ── Función de traducción ─────────────────────────────────────────────────────
export function switchLocale(lang: Locale) {
  if (!browser) return;

  locale.set(lang);

  if (lang === 'es') {
    // Restaurar al español: limpiar cookie y recargar
    document.cookie = 'googtrans=; path=/; max-age=0';
    document.cookie = `googtrans=; domain=.${window.location.hostname}; path=/; max-age=0`;
    window.location.reload();
  } else {
    // Intentar usar el widget ya cargado; si no, usar cookie + recarga
    const tryTranslate = (attempts = 0) => {
      const select = document.querySelector('.goog-te-combo') as HTMLSelectElement | null;
      if (select) {
        select.value = lang;
        select.dispatchEvent(new Event('change'));
      } else if (attempts < 20) {
        setTimeout(() => tryTranslate(attempts + 1), 150);
      } else {
        document.cookie = `googtrans=/es/${lang}; path=/`;
        window.location.reload();
      }
    };
    tryTranslate();
  }
}

// ── Traducciones de la UI (header / footer) ───────────────────────────────────
const translations = {
  es: {
    topbar: { help: 'Ayuda', contact: 'Contacto' },
    nav: {
      home: 'Inicio',
      collections: 'Colecciones Digitales',
      map: 'Mapa',
      research: 'Investigación',
      about: 'Acerca del Proyecto',
    },
    auth: {
      login: 'Iniciar sesión',
      logout: 'Cerrar sesión',
      profile: 'Mi Perfil',
      projects: 'Mis Proyectos',
      admin: 'Administración',
    },
    invitations: { title: 'Invitaciones', accept: 'Aceptar', decline: 'Rechazar' },
    search: { placeholder: 'Buscar en el archivo...' },
    branding: { subtitle: 'Universidad Católica del Norte', title: 'Fondo Robert Gerstmann' },
    footer: {
      nav: 'Navegación',
      legal: 'Legal y Contacto',
      collections: 'Colecciones',
      policies: 'Política de Privacidad y Uso',
      accessibility: 'Accesibilidad',
      rights: 'Todos los derechos reservados.',
    },
  },
  en: {
    topbar: { help: 'Help', contact: 'Contact' },
    nav: {
      home: 'Home',
      collections: 'Digital Collections',
      map: 'Map',
      research: 'Research',
      about: 'About the Project',
    },
    auth: {
      login: 'Log in',
      logout: 'Log out',
      profile: 'My Profile',
      projects: 'My Projects',
      admin: 'Administration',
    },
    invitations: { title: 'Invitations', accept: 'Accept', decline: 'Decline' },
    search: { placeholder: 'Search the archive...' },
    branding: { subtitle: 'Catholic University of the North', title: 'Robert Gerstmann Archive' },
    footer: {
      nav: 'Navigation',
      legal: 'Legal & Contact',
      collections: 'Collections',
      policies: 'Privacy & Usage Policy',
      accessibility: 'Accessibility',
      rights: 'All rights reserved.',
    },
  },
  de: {
    topbar: { help: 'Hilfe', contact: 'Kontakt' },
    nav: {
      home: 'Startseite',
      collections: 'Digitale Sammlungen',
      map: 'Karte',
      research: 'Forschung',
      about: 'Über das Projekt',
    },
    auth: {
      login: 'Anmelden',
      logout: 'Abmelden',
      profile: 'Mein Profil',
      projects: 'Meine Projekte',
      admin: 'Administration',
    },
    invitations: { title: 'Einladungen', accept: 'Annehmen', decline: 'Ablehnen' },
    search: { placeholder: 'Im Archiv suchen...' },
    branding: { subtitle: 'Katholische Universität des Nordens', title: 'Robert-Gerstmann-Archiv' },
    footer: {
      nav: 'Navigation',
      legal: 'Rechtliches & Kontakt',
      collections: 'Sammlungen',
      policies: 'Datenschutz & Nutzungsbedingungen',
      accessibility: 'Barrierefreiheit',
      rights: 'Alle Rechte vorbehalten.',
    },
  },
} as const;

export const t = derived(locale, ($locale) => translations[$locale]);
