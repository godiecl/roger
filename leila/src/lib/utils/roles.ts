export const roleLabel: Record<string, string> = {
  administrador: 'Administrador',
  curador: 'Curador',
  investigador: 'Investigador',
  digitalizador: 'Digitalizador',
  colaborador: 'Colaborador',
  sistema_ia: 'Sistema IA',
  usuario_estandar: 'Explorador',
};

export const roleBadge: Record<string, string> = {
  administrador: 'badge-error',
  curador: 'badge-warning',
  investigador: 'badge-info',
  digitalizador: 'badge-accent',
  colaborador: 'badge-secondary',
  sistema_ia: 'badge-neutral',
  usuario_estandar: 'badge-ghost',
};

export function getRoleLabel(role: string | undefined | null): string {
  if (!role) return '';
  return roleLabel[role] ?? role;
}
