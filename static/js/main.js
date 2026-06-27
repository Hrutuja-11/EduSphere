document.addEventListener('DOMContentLoaded', () => {
    // 1. Intersection Observer for Scroll Reveals
    const revealElements = document.querySelectorAll('.reveal');
    const observerOptions = {
        root: null,
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px' // Triggers slightly before element enters view
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                
                // If it is a group container, stagger the reveal of children items
                if (entry.target.classList.contains('reveal-group')) {
                    const children = entry.target.querySelectorAll('.reveal-item');
                    children.forEach((child, index) => {
                        child.style.transitionDelay = `${index * 0.1}s`;
                        child.classList.add('revealed');
                    });
                }
                
                observer.unobserve(entry.target); // Trigger once
            }
        });
    }, observerOptions);

    revealElements.forEach(el => revealObserver.observe(el));

    // 2. Glassmorphic Navbar Scroll Transform
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const handleScroll = () => {
            if (window.scrollY > 20) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll(); // Initial check on load
    }

    // 3. Mouse Movement Parallax on Hero Background Blobs
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        heroSection.addEventListener('mousemove', (e) => {
            const blobs = document.querySelectorAll('.hero-blob');
            const rect = heroSection.getBoundingClientRect();
            // Calculate mouse position relative to hero bounds (-0.5 to 0.5)
            const mouseX = (e.clientX - rect.left) / rect.width - 0.5;
            const mouseY = (e.clientY - rect.top) / rect.height - 0.5;

            blobs.forEach((blob, index) => {
                const multiplier = (index + 1) * 30; // Stagger factor for layered depth
                const tx = mouseX * multiplier;
                const ty = mouseY * multiplier;
                // Combine mouse movement with base floating animation
                blob.style.setProperty('--mouse-x', `${tx}px`);
                blob.style.setProperty('--mouse-y', `${ty}px`);
            });
        }, { passive: true });
    }
});
