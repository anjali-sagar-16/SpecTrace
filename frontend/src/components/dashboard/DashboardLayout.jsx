import { useState } from 'react';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { ConnectGithubModal } from './ConnectGithubModal';
import { OverviewView } from './views/OverviewView';
import { ProjectsView } from './views/ProjectsView';
import { RepositoriesView } from './views/RepositoriesView';
import { RequirementsView } from './views/RequirementsView';
import { ImpactAnalysisView } from './views/ImpactAnalysisView';
import { HistoryView } from './views/HistoryView';
import './Dashboard.css';

const SECTION_TITLES = {
  overview: 'Platform Overview',
  projects: 'Projects & Domains',
  repositories: 'Code Repositories',
  requirements: 'Software Requirements',
  'impact-analysis': 'Change Impact Analysis',
  history: 'Change History & Audit',
};

export function DashboardLayout({ onSignOut }) {
  const [activeSection, setActiveSection] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [isGithubModalOpen, setIsGithubModalOpen] = useState(false);

  const activeTitle = SECTION_TITLES[activeSection] || 'Dashboard';

  const renderActiveView = () => {
    switch (activeSection) {
      case 'overview':
        return (
          <OverviewView
            searchQuery={searchQuery}
            onOpenGithubModal={() => setIsGithubModalOpen(true)}
            onSelectSection={setActiveSection}
          />
        );
      case 'projects':
        return <ProjectsView onSelectSection={setActiveSection} />;
      case 'repositories':
        return (
          <RepositoriesView
            onOpenGithubModal={() => setIsGithubModalOpen(true)}
            onSelectSection={setActiveSection}
          />
        );
      case 'requirements':
        return <RequirementsView onSelectSection={setActiveSection} />;
      case 'impact-analysis':
        return <ImpactAnalysisView onSelectSection={setActiveSection} />;
      case 'history':
        return <HistoryView onSelectSection={setActiveSection} />;
      default:
        return (
          <OverviewView
            searchQuery={searchQuery}
            onOpenGithubModal={() => setIsGithubModalOpen(true)}
            onSelectSection={setActiveSection}
          />
        );
    }
  };

  return (
    <div className="dashboard-viewport">
      <Sidebar
        activeSection={activeSection}
        onSelectSection={setActiveSection}
        onOpenGithubModal={() => setIsGithubModalOpen(true)}
        onSignOut={onSignOut}
      />

      <div className="dashboard-main-area">
        <TopNav
          activeSectionTitle={activeTitle}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onOpenGithubModal={() => setIsGithubModalOpen(true)}
          onSignOut={onSignOut}
        />

        <main className="dashboard-content-scrollable">
          {renderActiveView()}
        </main>
      </div>

      <ConnectGithubModal
        isOpen={isGithubModalOpen}
        onClose={() => setIsGithubModalOpen(false)}
      />
    </div>
  );
}
