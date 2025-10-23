// Gestion optimisée des graphiques pour mobile
document.addEventListener('DOMContentLoaded', function() {
    
    // Gestion des images base64 pour mobile
    const graphImages = document.querySelectorAll('.graph-container img');
    
    graphImages.forEach(img => {
        // Ajouter un état de chargement
        const container = img.parentElement;
        container.classList.add('graph-loading');
        
        img.addEventListener('load', function() {
            container.classList.remove('graph-loading');
            this.style.opacity = '0';
            this.style.transition = 'opacity 0.5s ease-in';
            
            // Forcer le repaint
            void this.offsetWidth;
            
            this.style.opacity = '1';
        });
        
        img.addEventListener('error', function() {
            container.classList.remove('graph-loading');
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>Graphique non disponible</p>
                    <small>Rechargez la page</small>
                </div>
            `;
        });
        
        // Forcer le chargement si l'image est en cache
        if (img.complete) {
            img.dispatchEvent(new Event('load'));
        }
    });
    
    // Redimensionnement responsive des graphiques
    function handleResize() {
        graphImages.forEach(img => {
            const container = img.parentElement;
            const containerWidth = container.offsetWidth;
            
            // Ajuster la taille si nécessaire
            if (containerWidth < 300) {
                img.style.maxWidth = '100%';
            }
        });
    }
    
    // Écouter les changements de taille
    window.addEventListener('resize', handleResize);
    handleResize(); // Initial call
    
    // Gestion du cache pour mobile
    if ('serviceWorker' in navigator && 'caches' in window) {
        // Nettoyer le cache des graphiques périodiquement
        setInterval(() => {
            caches.keys().then(cacheNames => {
                cacheNames.forEach(cacheName => {
                    if (cacheName.includes('graph')) {
                        caches.delete(cacheName);
                    }
                });
            });
        }, 24 * 60 * 60 * 1000); // Tous les jours
    }
});