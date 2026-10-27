import { useEffect } from 'react';
import Skip from './components/Skip.jsx';
import Loader from './components/Loader.jsx';
import Progress from './components/Progress.jsx';
import Grain from './components/Grain.jsx';
import Nav from './components/Nav.jsx';
import Mmenu from './components/Mmenu.jsx';
import Hero from './components/Hero.jsx';
import Proof from './components/Proof.jsx';
import Problem from './components/Problem.jsx';
import Results from './components/Results.jsx';
import Move from './components/Move.jsx';
import Demo from './components/Demo.jsx';
import Platform from './components/Platform.jsx';
import Trust from './components/Trust.jsx';
import Recon from './components/Recon.jsx';
import Story from './components/Story.jsx';
import Case from './components/Case.jsx';
import Faq from './components/Faq.jsx';
import Cta from './components/Cta.jsx';
import Footer from './components/Footer.jsx';

// site.js is the original motion layer (GSAP ScrollTrigger/SplitText/DrawSVG + anime.js + Lenis).
// It queries the DOM once at boot, so it is injected after React has mounted the markup.
function useSiteMotion() {
  useEffect(() => {
    if (document.querySelector('script[data-site-js]')) return;
    const s = document.createElement('script');
    s.src = '/assets/js/site.js';
    s.dataset.siteJs = '';
    document.body.appendChild(s);
  }, []);
}

export default function App() {
  useSiteMotion();
  return (
    <>
      <Skip />
      <Loader />
      <Progress />
      <Grain />
      <Nav />
      <Mmenu />
      <main id="main">
        <Hero />
        <Proof />
        <Problem />
        <Results />
        <Move />
        <Demo />
        <Platform />
        <Trust />
        <Recon />
        <Story />
        <Case />
        <Faq />
        <Cta />
      </main>
      <Footer />
    </>
  );
}
