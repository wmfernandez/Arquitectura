(function() {
    function injectStyle() {
        // Asegurarnos de que OpenLayers esté cargado
        if (typeof ol !== 'undefined' && ol.Map && ol.Map.prototype.addLayer) {
            console.log("Inyectando estilos personalizados GIS para Padron (Método addLayer)");
            
            if (ol.Map.prototype.__patchedForPadron) return;
            
            const originalAddLayer = ol.Map.prototype.addLayer;
            
            ol.Map.prototype.addLayer = function(layer) {
                // Llamamos a la función original
                originalAddLayer.call(this, layer);
                
                // Si la capa añadida es un Vector (la que contiene los polígonos)
                if (layer && layer instanceof ol.layer.Vector) {
                    const numeroInput = document.getElementById('id_numero_padron');
                    // Verificamos que estemos en la vista de Padron
                    if (numeroInput) {
                        const updateStyle = () => {
                            layer.setStyle(function(feature) {
                                return new ol.style.Style({
                                    fill: new ol.style.Fill({
                                        color: 'rgba(113, 174, 220, 0.8)' // #71aedc al 80%
                                    }),
                                    stroke: new ol.style.Stroke({
                                        color: 'rgba(30, 63, 102, 1)',
                                        width: 2
                                    }),
                                    text: new ol.style.Text({
                                        text: numeroInput.value || '',
                                        font: 'bold 16px Arial',
                                        fill: new ol.style.Fill({ color: '#ffffff' }),
                                        stroke: new ol.style.Stroke({ color: '#000000', width: 3 }),
                                        overflow: true,
                                        placement: 'point'
                                    })
                                });
                            });
                        };
                        
                        // Aplicar el estilo
                        updateStyle();
                        
                        // Si el usuario cambia el número de padrón, actualizar el mapa
                        numeroInput.addEventListener('input', () => {
                            updateStyle();
                            layer.changed();
                        });
                    }
                }
            };
            
            ol.Map.prototype.__patchedForPadron = true;
        } else {
            // Reintentar si OpenLayers aún no ha cargado
            setTimeout(injectStyle, 50);
        }
    }
    
    injectStyle();
})();
