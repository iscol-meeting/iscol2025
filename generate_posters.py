#!/usr/bin/env python3
"""
Generate posters.html from posters.csv
"""

import csv
from pathlib import Path

def load_posters(csv_path):
    """Load posters from CSV and group by session."""
    posters_by_session = {1: [], 2: [], 3: []}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            session_id = int(row['Poster Session ID'])
            posters_by_session[session_id].append({
                'title': row['title'],
                'authors': row['Authors']
            })
    
    return posters_by_session

def generate_html(posters_by_session):
    """Generate HTML for the posters page."""
    
    # Session times from the program
    session_times = {
        1: "10:15 - 11:15",
        2: "13:45 - 14:45",
        3: "16:40 - 17:40"
    }
    
    html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Posters — ISCOL 2025</title>
    <meta
      name="description"
      content="ISCOL 2025 Accepted Posters. December 18th, 2025 at Bar-Ilan University."
    />
    
    <!-- SEO Meta Tags -->
    <meta name="keywords" content="ISCOL, computational linguistics, NLP, natural language processing, Israel, Bar-Ilan University, conference, seminar, posters" />
    <meta name="author" content="ISCOL 2025 Organizing Committee" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="https://iscol-meeting.github.io/iscol2025/posters.html" />
    
    <!-- Favicon and Icons -->
    <link rel="icon" type="image/png" href="./assets/iscol-fav.png" />
    
    <!-- Preload critical resources -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />
    
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <!-- Skip Links for Accessibility -->
    <div class="skip-links">
      <a href="#main-content" class="skip-link">Skip to main content</a>
      <a href="#nav-menu" class="skip-link">Skip to navigation</a>
    </div>

    <header class="site-header" role="banner">
      <div class="container header-inner">
        <a href="./index.html" class="brand">ISCOL 2025</a>
        <nav class="nav" aria-label="Primary navigation" role="navigation">
          <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu">☰</button>
          <ul id="nav-menu" class="nav-list">
            <li><a href="./index.html">Home</a></li>
            <li><a href="./index.html#cfp">Call for Papers</a></li>
            <li><a href="./program.html">Program</a></li>
            <li><a href="./posters.html">Posters</a></li>
            <li><a href="./index.html#organizers">Committee</a></li>
            <li><a href="./index.html#faq">FAQ</a></li>
            <li><a href="./index.html#sponsors">Sponsors</a></li>
          </ul>
        </nav>
      </div>
    </header>

    <main id="main-content" role="main">
      <section id="posters" class="section">
        <div class="container">
          <h1>Accepted Posters</h1>
          <p class="subtitle">ISCOL 2025 • December 18th, 2025</p>

          <!-- Mobile Session Tabs -->
          <div class="session-tabs">
            <button class="session-tab active" data-session="1">Session 1<br><span class="tab-time">10:15 - 11:15</span></button>
            <button class="session-tab" data-session="2">Session 2<br><span class="tab-time">13:45 - 14:45</span></button>
            <button class="session-tab" data-session="3">Session 3<br><span class="tab-time">16:40 - 17:40</span></button>
          </div>

          <div class="sessions-grid">
'''

    # Generate sections for each poster session
    for session_id in sorted(posters_by_session.keys()):
        posters = posters_by_session[session_id]
        time = session_times[session_id]
        
        html += f'''
            <div class="session-column" data-session-content="{session_id}">
              <div class="session-header">
                <h2 id="session-{session_id}">Session {session_id} <span class="session-time">({time})</span></h2>
              </div>
              <div class="posters-list">
'''
        
        for poster in posters:
            # Escape HTML in title and authors
            title = poster['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            authors = poster['authors'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            html += f'''            <div class="poster-item">
              <div class="poster-title">{title}</div>
              <div class="poster-authors">{authors}</div>
            </div>
'''
        
        html += '''              </div>
            </div>
'''

    html += '''          </div>
        </div>
      </section>
    </main>

    <footer class="site-footer" role="contentinfo">
      <div class="container footer-inner">
        <div>
          <strong>ISCOL 2025</strong>
          <div>Bar-Ilan University • Israel</div>
        </div>
        <div class="footer-links">
          <a href="./index.html">Home</a>
          <a href="./index.html#cfp">CFP</a>
          <a href="./program.html">Program</a>
          <a href="./posters.html">Posters</a>
          <a href="./index.html#organizers">Committee</a>
          <a href="./index.html#faq">FAQ</a>
          <a href="./index.html#sponsors">Sponsors</a>
        </div>
      </div>
    </footer>

    <!-- Back to Top Button -->
    <button class="back-to-top" id="backToTop" aria-label="Back to top">
      ↑
    </button>

    <script>
      // Session tabs for mobile
      const sessionTabs = document.querySelectorAll('.session-tab');
      const sessionColumns = document.querySelectorAll('.session-column');
      
      // Initialize first session as active on page load
      if (sessionColumns.length > 0) {
        sessionColumns[0].classList.add('active');
      }
      
      sessionTabs.forEach(tab => {
        tab.addEventListener('click', () => {
          const sessionId = tab.dataset.session;
          
          // Remove active class from all tabs and columns
          sessionTabs.forEach(t => t.classList.remove('active'));
          sessionColumns.forEach(c => c.classList.remove('active'));
          
          // Add active class to clicked tab and corresponding column
          tab.classList.add('active');
          document.querySelector(`[data-session-content="${sessionId}"]`).classList.add('active');
        });
      });
      
      // Mobile navigation toggle
      const toggle = document.querySelector('.nav-toggle');
      const menu = document.getElementById('nav-menu');
      if (toggle && menu) {
        toggle.addEventListener('click', () => {
          const expanded = toggle.getAttribute('aria-expanded') === 'true';
          toggle.setAttribute('aria-expanded', String(!expanded));
          menu.classList.toggle('open');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
          if (!toggle.contains(e.target) && !menu.contains(e.target)) {
            toggle.setAttribute('aria-expanded', 'false');
            menu.classList.remove('open');
          }
        });

        // Close menu when pressing Escape
        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape' && menu.classList.contains('open')) {
            toggle.setAttribute('aria-expanded', 'false');
            menu.classList.remove('open');
            toggle.focus();
          }
        });
      }

      // Back to top button functionality
      const backToTopButton = document.getElementById('backToTop');
      
      function toggleBackToTopButton() {
        if (window.scrollY > 300) {
          backToTopButton.classList.add('visible');
        } else {
          backToTopButton.classList.remove('visible');
        }
      }

      // Show/hide back to top button on scroll
      window.addEventListener('scroll', toggleBackToTopButton);

      // Smooth scroll to top when button is clicked
      backToTopButton.addEventListener('click', () => {
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
      });

      // Initialize back to top button visibility
      toggleBackToTopButton();
    </script>
  </body>
</html>
'''
    
    return html

def main():
    """Main function to generate posters.html."""
    script_dir = Path(__file__).parent
    csv_path = script_dir / 'assets' / 'posters.csv'
    output_path = script_dir / 'posters.html'
    
    print(f"Loading posters from {csv_path}...")
    posters_by_session = load_posters(csv_path)
    
    # Print statistics
    for session_id in sorted(posters_by_session.keys()):
        count = len(posters_by_session[session_id])
        print(f"  Session {session_id}: {count} posters")
    
    print(f"\nGenerating HTML...")
    html = generate_html(posters_by_session)
    
    print(f"Writing to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Successfully generated {output_path}")

if __name__ == '__main__':
    main()
