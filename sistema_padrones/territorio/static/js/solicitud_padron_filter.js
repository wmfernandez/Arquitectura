document.addEventListener('DOMContentLoaded', function () {
    const tipoSelect = document.getElementById('id_filtro_tipo_padron');
    const locSelect = document.getElementById('id_filtro_localidad');
    const padronInput = document.getElementById('id_padron');
    const lookupAnchor = document.getElementById('lookup_id_padron');

    if (!tipoSelect || !locSelect || !padronInput || !lookupAnchor) return;

    // Create a container for the details
    const detailsSpan = document.createElement('span');
    detailsSpan.style.marginLeft = '10px';
    detailsSpan.style.fontWeight = 'bold';
    detailsSpan.style.color = '#005a9e';
    lookupAnchor.parentNode.insertBefore(detailsSpan, lookupAnchor.nextSibling);

    function updateLookupHref() {
        let baseHref = '/admin/territorio/padron/?_to_field=id';
        if (tipoSelect.value) {
            baseHref += '&tipo_padron__id__exact=' + tipoSelect.value;
            const tipoText = tipoSelect.options[tipoSelect.selectedIndex].text;
            if (tipoText.toLowerCase() === 'urbano' && locSelect.value) {
                baseHref += '&localidad=' + encodeURIComponent(locSelect.value);
            }
        }
        lookupAnchor.href = baseHref;
    }

    function toggleLocalidad() {
        const tipoText = tipoSelect.options[tipoSelect.selectedIndex]?.text || '';
        const locRow = locSelect.closest('.form-row');
        if (tipoText.toLowerCase() === 'urbano') {
            locRow.style.display = 'block';
        } else {
            locRow.style.display = 'none';
            locSelect.value = '';
        }
        updateLookupHref();
    }

    function fetchPadronDetails() {
        const padronId = padronInput.value;
        if (!padronId) {
            detailsSpan.textContent = '';
            return;
        }

        // Hide native Django strong tag if it exists
        const nativeStrong = lookupAnchor.parentNode.querySelector('strong');
        if (nativeStrong) nativeStrong.style.display = 'none';

        detailsSpan.textContent = 'Cargando datos...';
        fetch('/api/padron/detalles/' + padronId + '/')
            .then(res => res.json())
            .then(data => {
                if (data.detalles) {
                    detailsSpan.textContent = data.detalles;
                } else {
                    detailsSpan.textContent = '';
                }
                const nativeStrong = lookupAnchor.parentNode.querySelector('strong');
                if (nativeStrong) nativeStrong.style.display = 'none';
            })
            .catch(() => {
                detailsSpan.textContent = '';
            });
    }

    tipoSelect.addEventListener('change', toggleLocalidad);
    locSelect.addEventListener('change', updateLookupHref);

    // Override dismissRelatedLookupPopup to fetch details immediately
    const originalDismiss = window.dismissRelatedLookupPopup;
    if (originalDismiss) {
        window.dismissRelatedLookupPopup = function (win, chosenId) {
            originalDismiss(win, chosenId);
            setTimeout(fetchPadronDetails, 100);
        };
    } else {
        padronInput.addEventListener('change', fetchPadronDetails);
    }

    // Initialize state
    toggleLocalidad();
    fetchPadronDetails();
});
