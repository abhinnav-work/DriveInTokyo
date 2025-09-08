// Drive in Tokyo - Interactive Features
document.addEventListener('DOMContentLoaded', function() {
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Navbar background change on scroll
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Fade in animation for elements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observe elements for fade-in animation
    const fadeElements = document.querySelectorAll('.car-card, .section-title, .about-content, .contact-info');
    fadeElements.forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });

    // Car card hover effects
    const carCards = document.querySelectorAll('.car-card');
    carCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Open full-res (prefer PNG) with graceful fallbacks
    function openFullResFromImg(imgEl) {
        const currentSrc = imgEl.currentSrc || imgEl.src || '';
        const alt = imgEl.alt || '';
        const normalized = currentSrc.replace(/\\/g, '/');

        // Derive potential full-res paths
        const candidates = [];
        // If optimized path (webp), map to assets counterpart
        if (normalized.includes('assets_optimized/')) {
            const base = normalized
                .replace('assets_optimized/', 'assets/')
                .replace(/\.webp$/i, '')
                .replace(/\.jpg$/i, '')
                .replace(/\.jpeg$/i, '')
                .replace(/\.png$/i, '');
            candidates.push(base + '.png', base + '.JPG', base + '.jpg', base + '.jpeg');
        }
        // If already assets/ path, try png first, then original
        if (normalized.includes('assets/')) {
            const base2 = normalized.replace(/\.jpe?g$/i, '').replace(/\.png$/i, '');
            candidates.push(base2 + '.png', normalized);
        }
        // Fallback: current
        if (!candidates.includes(normalized)) candidates.push(normalized);

        createImageModalWithFallback(candidates, alt);
    }

    // Bind gallery clicks
    const galleryImages = document.querySelectorAll('.gallery img');
    galleryImages.forEach(img => {
        img.addEventListener('click', function() {
            openFullResFromImg(this);
        });
    });

    // Bind car section clicks
    const carImages = document.querySelectorAll('.car-image img');
    carImages.forEach(img => {
        img.addEventListener('click', function() {
            openFullResFromImg(this);
        });
    });

    // Contact form handling
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const name = this.querySelector('input[type="text"]').value;
            const email = this.querySelector('input[type="email"]').value;
            const experience = this.querySelector('select').value;
            const message = this.querySelector('textarea').value;
            
            // Simple validation
            if (!name || !email || !message) {
                showNotification('Please fill in all required fields.', 'error');
                return;
            }
            
            // Simulate form submission
            showNotification('Thank you for your message! We will get back to you soon.', 'success');
            this.reset();
        });
    }

    // Initialize Bootstrap carousel with autoplay
    const carousel = document.querySelector('#mainCarousel');
    if (carousel) {
        // Initialize Bootstrap carousel
        const bsCarousel = new bootstrap.Carousel(carousel, {
            interval: 4000, // 4 seconds
            ride: 'carousel',
            pause: false, // Don't pause on hover
            wrap: true
        });
        
        // Ensure autoplay continues
        carousel.addEventListener('slide.bs.carousel', function () {
            // Carousel is working
        });
        
        // Optional: Pause on hover for better UX
        carousel.addEventListener('mouseenter', function() {
            bsCarousel.pause();
        });
        
        carousel.addEventListener('mouseleave', function() {
            bsCarousel.cycle();
        });

        // Swipe support for touch devices
        let touchStartX = 0;
        let touchEndX = 0;
        const threshold = 50; // px
        carousel.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        carousel.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            const deltaX = touchEndX - touchStartX;
            if (Math.abs(deltaX) > threshold) {
                if (deltaX > 0) {
                    bsCarousel.prev();
                } else {
                    bsCarousel.next();
                }
            }
        });
    }

    // Removed parallax on hero to prevent scroll jank

    // Loading screen
    window.addEventListener('load', function() {
        const loadingScreen = document.querySelector('.loading');
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500);
        }
    });

    // Build masonry gallery from metadata
    try {
        const delayedOverlay = document.getElementById('delayedLoading');
        const showDelay = setTimeout(() => {
            if (delayedOverlay) delayedOverlay.style.display = 'flex';
        }, 1000);

        function getEmbeddedMeta() {
            const tag = document.getElementById('gallery-metadata');
            if (!tag) return null;
            try { return JSON.parse(tag.textContent); } catch { return null; }
        }

        const embedded = getEmbeddedMeta();
        const metaPromise = embedded ? Promise.resolve(embedded) : fetch('scripts/image_metadata.json').then(r => r.json());

        metaPromise
            .then(meta => {
                const galleryEl = document.getElementById('masonryGallery');
                const loadMoreBtn = document.getElementById('loadMoreGallery');
                if (!galleryEl) return;

                // Preferred order: feature landscapes first, then others
                const entries = Object.entries(meta);
                entries.sort((a, b) => {
                    const pa = a[1]?.layout?.priority === 'feature' ? 1 : 0;
                    const pb = b[1]?.layout?.priority === 'feature' ? 1 : 0;
                    if (pa !== pb) return pb - pa;
                    const arA = a[1]?.aspectRatio || 1;
                    const arB = b[1]?.aspectRatio || 1;
                    return (arB - arA);
                });

                // Only include gallery images (skip logo and landing-only items)
                const skipKeys = new Set(['logo', 'logo_bg_remove']);
                const galleryEntries = entries.filter(([key, data]) => {
                    if (skipKeys.has(key)) return false;
                    const opt = (data?.paths?.optimized || '').replace(/\\/g, '/');
                    const orig = (data?.paths?.original || '').replace(/\\/g, '/');
                    return opt.includes('/gallery/') || orig.includes('/gallery/');
                });

                let cursor = 0;
                const PAGE_SIZE = 8;

                function appendItems(count) {
                    const slice = galleryEntries.slice(cursor, cursor + count);
                    for (const [key, data] of slice) {
                        const normalizedOpt = (data?.paths?.optimized || '').replace(/\\/g, '/');
                        const normalizedOrig = (data?.paths?.original || '').replace(/\\/g, '/');

                        const item = document.createElement('div');
                        item.className = 'masonry-item';

                        const picture = document.createElement('picture');
                        const source = document.createElement('source');
                        source.type = 'image/webp';
                        source.srcset = normalizedOpt;
                        const img = document.createElement('img');
                        img.alt = key.replace(/_/g, ' ');
                        img.src = normalizedOrig || normalizedOpt;
                        img.loading = 'lazy';
                        img.decoding = 'async';
                        img.sizes = '(max-width: 576px) 100vw, (max-width: 992px) 50vw, 25vw';

                        picture.appendChild(source);
                        picture.appendChild(img);
                        item.appendChild(picture);
                        galleryEl.appendChild(item);
                    }
                    cursor += slice.length;
                    if (loadMoreBtn && cursor >= galleryEntries.length) {
                        loadMoreBtn.style.display = 'none';
                    }
                }

                appendItems(PAGE_SIZE);

                if (loadMoreBtn) {
                    loadMoreBtn.addEventListener('click', () => appendItems(PAGE_SIZE));
                }
            })
            .catch(() => {})
            .finally(() => {
                clearTimeout(showDelay);
                const delayedOverlay = document.getElementById('delayedLoading');
                if (delayedOverlay) delayedOverlay.style.display = 'none';
            });
    } catch (e) {
        // ignore
    }
});

// Utility Functions
function createImageModalWithFallback(srcCandidates, alt) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        cursor: pointer;
    `;
    
    // Create image
    const img = document.createElement('img');
    img.alt = alt;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
        border-radius: 10px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    `;

    // Load with fallbacks
    let idx = 0;
    function tryNext() {
        if (idx >= srcCandidates.length) return; // give up
        img.src = srcCandidates[idx++];
    }
    img.addEventListener('error', tryNext, { once: false });
    tryNext();
    
    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = `
        position: absolute;
        top: 20px;
        right: 30px;
        background: none;
        border: none;
        color: white;
        font-size: 40px;
        cursor: pointer;
        z-index: 10001;
    `;
    
    modal.appendChild(img);
    modal.appendChild(closeBtn);
    document.body.appendChild(modal);
    
    // Close modal functionality
    function closeModal() {
        modal.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(modal);
        }, 300);
    }
    
    modal.addEventListener('click', closeModal);
    closeBtn.addEventListener('click', closeModal);
    
    // Prevent image click from closing modal
    img.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // ESC key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Add loading screen to HTML if not present
if (!document.querySelector('.loading')) {
    const loadingScreen = document.createElement('div');
    loadingScreen.className = 'loading';
    loadingScreen.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(loadingScreen);
}