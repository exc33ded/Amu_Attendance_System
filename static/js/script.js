// Smooth Scrolling Effect
document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.querySelector(".navbar");
    
    window.addEventListener("scroll", function () {
        if (window.scrollY > 50) {
            navbar.classList.add("shadow-sm");
        } else {
            navbar.classList.remove("shadow-sm");
        }
    });
});


// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});


// Button Hover Effect
document.querySelectorAll(".btn").forEach(button => {
    button.addEventListener("mouseenter", function () {
        this.classList.add("shadow-lg");
    });
    button.addEventListener("mouseleave", function () {
        this.classList.remove("shadow-lg");
    });
});

// Optimized preloader
document.addEventListener('DOMContentLoaded', function() {
    const preloader = document.getElementById('preloader');
    if (preloader) {
        // Hide preloader after page is fully loaded
        window.addEventListener('load', function() {
            requestAnimationFrame(() => {
                preloader.style.opacity = '0';
                setTimeout(() => {
                    preloader.style.display = 'none';
                }, 300);
            });
        });

        // Fallback: Hide preloader after 2 seconds if page doesn't load
        setTimeout(() => {
            if (preloader.style.display !== 'none') {
                requestAnimationFrame(() => {
                    preloader.style.opacity = '0';
                    setTimeout(() => {
                        preloader.style.display = 'none';
                    }, 300);
                });
            }
        }, 2000);
    }
});

// Debounced scroll handler
let scrollTimeout;
window.addEventListener('scroll', function() {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }

        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            if (window.scrollY > 300) {
                backToTop.classList.add('active');
            } else {
                backToTop.classList.remove('active');
            }
        }
    }, 10);
});

// Optimized back to top button
const backToTop = document.getElementById('backToTop');
if (backToTop) {
    backToTop.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Optimized smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Optimized form validation
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        form.classList.add('was-validated');
    });
});

// Optimized stats counter with Intersection Observer
const stats = document.querySelectorAll('.stat-item span');
if (stats.length > 0) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const finalValue = parseInt(target.textContent);
                let currentValue = 0;
                const duration = 1500; // Reduced duration
                const increment = finalValue / (duration / 16);
                
                const counter = setInterval(() => {
                    currentValue += increment;
                    if (currentValue >= finalValue) {
                        target.textContent = finalValue;
                        clearInterval(counter);
                    } else {
                        target.textContent = Math.floor(currentValue);
                    }
                }, 16);
                
                observer.unobserve(target);
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach(stat => observer.observe(stat));
}

// Optimized mobile menu
const navbarToggler = document.querySelector('.navbar-toggler');
const navbarCollapse = document.querySelector('.navbar-collapse');

if (navbarToggler && navbarCollapse) {
    navbarToggler.addEventListener('click', function() {
        navbarCollapse.classList.toggle('show');
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
            navbarCollapse.classList.remove('show');
        }
    });
}

// Optimized newsletter form
const newsletterForm = document.querySelector('.newsletter-form');
if (newsletterForm) {
    newsletterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const emailInput = this.querySelector('input[type="email"]');
        const email = emailInput.value;
        
        // Here you would typically send the email to your backend
        console.log('Subscribing email:', email);
        
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.className = 'alert alert-success mt-3';
        successMessage.textContent = 'Thank you for subscribing!';
        this.appendChild(successMessage);
        
        // Clear input
        emailInput.value = '';
        
        // Remove success message after 3 seconds
        setTimeout(() => {
            successMessage.remove();
        }, 3000);
    });
}

// Optimized animations
const animatedElements = document.querySelectorAll('[data-aos]');
if (animatedElements.length > 0) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fadeIn');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    animatedElements.forEach(element => observer.observe(element));
}
