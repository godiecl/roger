/**
 * Projects store
 * Manages project and member state
 */
import { writable, derived } from 'svelte/store';
import type { Project, ProjectMember } from '$lib/types';

interface ProjectsState {
  projects: Project[];
  currentProject: Project | null;
  members: ProjectMember[];
  loading: boolean;
  error: string | null;
}

const initialState: ProjectsState = {
  projects: [],
  currentProject: null,
  members: [],
  loading: false,
  error: null
};

function createProjectsStore() {
  const { subscribe, set, update } = writable<ProjectsState>(initialState);

  return {
    subscribe,

    setProjects(projects: Project[]) {
      update(state => ({ ...state, projects, error: null }));
    },

    setCurrentProject(project: Project | null) {
      update(state => ({ ...state, currentProject: project, error: null }));
    },

    setMembers(members: ProjectMember[]) {
      update(state => ({ ...state, members }));
    },

    addProject(project: Project) {
      update(state => ({
        ...state,
        projects: [project, ...state.projects]
      }));
    },

    removeProject(projectId: number) {
      update(state => ({
        ...state,
        projects: state.projects.filter(p => p.id !== projectId)
      }));
    },

    addMember(member: ProjectMember) {
      update(state => ({
        ...state,
        members: [...state.members, member]
      }));
    },

    removeMember(userId: number) {
      update(state => ({
        ...state,
        members: state.members.filter(m => m.user_id !== userId)
      }));
    },

    setLoading(loading: boolean) {
      update(state => ({ ...state, loading }));
    },

    setError(error: string | null) {
      update(state => ({ ...state, error }));
    },

    reset() {
      set(initialState);
    }
  };
}

export const projectsStore = createProjectsStore();

export const hasProjects = derived(
  projectsStore,
  $store => $store.projects.length > 0
);
