// Script de diagnostic pour les graphiques mobiles
function diagnoseCharts() {
    const evolutionImg = document.querySelector('#evolutionChart img');
    const categoriesImg = document.querySelector('#categoriesChart img');
    
    console.log('Diagnostic des graphiques:');
    console.log('Évolution:', evolutionImg ? 'Présent' : 'Absent');
    console.log('Catégories:', categoriesImg ? 'Présent' : 'Absent');
    
    if (evolutionImg) {
        console.log('Src Évolution:', evolutionImg.src.substring(0, 100) + '...');
        console.log('Taille Évolution:', evolutionImg.naturalWidth + 'x' + evolutionImg.naturalHeight);
    }
    
    if (categoriesImg) {
        console.log('Src Catégories:', categoriesImg.src.substring(0, 100) + '...');
        console.log('Taille Catégories:', categoriesImg.naturalWidth + 'x' + categoriesImg.naturalHeight);
    }
    
    // Test de performance
    const startTime = performance.now();
    const testImage = new Image();
    testImage.onload = function() {
        const loadTime = performance.now() - startTime;
        console.log('Temps de chargement test:', loadTime + 'ms');
    };
    testImage.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
}

// Exécuter le diagnostic au chargement
document.addEventListener('DOMContentLoaded', diagnoseCharts);