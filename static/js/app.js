document.addEventListener('DOMContentLoaded', () => {
    const state = {
        mainData: [],
        demographicsData: [],
        policeData: [],
        globalMainData: [],
        globalPoliceData: [], // Stores full dataset for client-side filtering if needed

        allCrimeTypes: [],
        allYears: [],

        // Decoupled Filters
        filters: {
            main: { year: '', province: '', district: '' },
            demo: { year: '', province: '' },
            police: { year: '', province: '' },
            prediction: { year: '2082', province: '', district: '' }
        },

        charts: {},
        currentChartType: 'pie'
    };

    const elements = {
        // Tabs
        tabs: document.querySelectorAll('.nav-tab'),
        panes: document.querySelectorAll('.tab-pane'),

        // Main Crime Elements
        mainYear: document.getElementById('mainYear'),
        mainProvince: document.getElementById('mainProvince'),
        mainDistrict: document.getElementById('mainDistrict'),
        mainSearchBtn: document.getElementById('mainSearchBtn'),
        mainCrimeInsight: document.getElementById('mainCrimeInsight'),

        // Buttons
        btnPie: document.getElementById('btnPie'),
        btnBar: document.getElementById('btnBar'),

        // Demographics Elements
        demoYear: document.getElementById('demoYear'),
        demoProvince: document.getElementById('demoProvince'),
        demoSearchBtn: document.getElementById('demoSearchBtn'),

        demFemalePct: document.getElementById('demFemalePct'),
        demFemaleCount: document.getElementById('demFemaleCount'),
        demMalePct: document.getElementById('demMalePct'),
        demMaleCount: document.getElementById('demMaleCount'),
        demUnknownPct: document.getElementById('demUnknownPct'),
        demUnknownCount: document.getElementById('demUnknownCount'),
        eduStatsContainer: document.getElementById('eduStatsContainer'),
        relStatsContainer: document.getElementById('relStatsContainer'),
        ageStatsContainer: document.getElementById('ageStatsContainer'),
        knownOffenderVal: document.getElementById('knownOffenderVal'),

        // Police Elements
        polYear: document.getElementById('polYear'),
        polProvince: document.getElementById('polProvince'),
        polSearchBtn: document.getElementById('polSearchBtn'),

        polOpenedVal: document.getElementById('polOpenedVal'),
        polOpenedPct: document.getElementById('polOpenedPct'),
        polClosedVal: document.getElementById('polClosedVal'),
        polClosedPct: document.getElementById('polClosedPct'),

        // Combined (Consolidated)
        combTotalCases: document.getElementById('combTotalCases'),
        combClearanceRate: document.getElementById('combClearanceRate'),
        combTopCrime: document.getElementById('combTopCrime'),
        combActiveCases: document.getElementById('combActiveCases'),
        combRatio: document.getElementById('combRatio'),
        combRisk: document.getElementById('combRisk'),
        combTrend: document.getElementById('combTrend'),

        // Prediction Elements
        predYear: document.getElementById('predYear'),
        predProvince: document.getElementById('predProvince'),
        predDistrict: document.getElementById('predDistrict'),
        predBtn: document.getElementById('predBtn'),
        predictionResults: document.getElementById('predictionResults'),
        predSafetyStatus: document.getElementById('predSafetyStatus'),
        safetyCard: document.getElementById('safetyCard'),
        predTargetYearLabel: document.getElementById('predTargetYearLabel'),
        predTotalCount: document.getElementById('predTotalCount'),
        risingCrimesList: document.getElementById('risingCrimesList'),
    };

    async function init() {
        setupTabs();
        setupFilters();

        const [filtersRes, statsRes, crimeTypesRes] = await Promise.all([
            fetch('/api/filters'),
            fetch('/api/dashboard/stats'),
            fetch('/api/crimetypes')
        ]);
        const filterOptions = await filtersRes.json();
        const stats = await statsRes.json();
        state.allCrimeTypes = await crimeTypesRes.json();
        state.allYears = filterOptions.years;

        // Populate independent filters
        populateDropdowns(elements.mainYear, state.allYears);
        populateDropdowns(elements.demoYear, state.allYears);
        populateDropdowns(elements.polYear, state.allYears);

        populateDropdowns(elements.mainProvince, filterOptions.provinces);
        populateDropdowns(elements.demoProvince, filterOptions.provinces);
        populateDropdowns(elements.polProvince, filterOptions.provinces);
        populateDropdowns(elements.predProvince, filterOptions.provinces);

        // Store global stats/data
        state.globalStats = stats;
        await fetchAllData();

        // Initial Render
        updateMainDashboard();
        updateDemoDashboard();
        updatePoliceDashboard();
        renderCombinedView(state.globalMainData, state.globalPoliceData, state.globalStats);
    }

    function setupTabs() {
        // Sub-tabs (Home view)
        // Sub-tabs (Home view)
        elements.tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                elements.tabs.forEach(t => t.classList.remove('active'));

                // Hide all panes
                elements.panes.forEach(p => p.classList.remove('active'));

                // Activate clicked tab
                tab.classList.add('active');
                const targetId = tab.dataset.tab;
                document.getElementById(targetId).classList.add('active');

                // Trigger re-render if switching to specific tabs (fixes Chart.js hidden canvas issue)
                if (targetId === 'combined') {
                    renderCombinedView(state.globalMainData, state.globalPoliceData, state.globalStats);
                } else if (targetId === 'demographics') {
                    updateDemoDashboard();
                } else if (targetId === 'police') {
                    updatePoliceDashboard();
                } else if (targetId === 'main-crime') {
                    // resize main chart if needed
                    if (state.charts['crimeTypeChart']) state.charts['crimeTypeChart'].resize();
                }
            });
        });

        // Top Navigation Wiring
        const navLinks = document.querySelectorAll('.nav-link');
        const navTabsContainer = document.querySelector('.nav-tabs');

        if (navLinks.length >= 3) {
            const homeLink = navLinks[0];
            const predLink = navLinks[1];
            const alertLink = navLinks[2];

            homeLink.addEventListener('click', () => {
                homeLink.classList.add('active');
                predLink.classList.remove('active');
                alertLink.classList.remove('active');
                navTabsContainer.style.display = 'flex';

                // Show Home Panes
                const activeSubTab = document.querySelector('.nav-tab.active');
                if (activeSubTab) activeSubTab.click();
                else document.querySelector('[data-tab="main-crime"]').click();

                // Hide others
                document.getElementById('prediction').classList.remove('active');
                document.getElementById('alert').classList.remove('active');
            });

            predLink.addEventListener('click', () => {
                predLink.classList.add('active');
                homeLink.classList.remove('active');
                alertLink.classList.remove('active');
                navTabsContainer.style.display = 'none';

                elements.panes.forEach(p => p.classList.remove('active'));
                document.getElementById('prediction').classList.add('active');
                document.getElementById('alert').classList.remove('active');
            });

            alertLink.addEventListener('click', () => {
                alertLink.classList.add('active');
                homeLink.classList.remove('active');
                predLink.classList.remove('active');
                navTabsContainer.style.display = 'none';

                elements.panes.forEach(p => p.classList.remove('active'));
                document.getElementById('prediction').classList.remove('active');
                document.getElementById('alert').classList.add('active');

                // Initialize Map if not already done
                if (!window.mapInitialized) {
                    initMap();
                    window.mapInitialized = true;
                }
                // Resize map after container is visible
                setTimeout(() => { if (window.nepalMap) window.nepalMap.invalidateSize(); }, 100);
            });
        }
    }

    function initMap() {
        // Initialize Leaflet Map
        window.nepalMap = L.map('nepalMap').setView([28.3949, 84.1240], 7); // Center of Nepal

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap attributes'
        }).addTo(window.nepalMap);

        // Load GeoJSON
        fetch('/static/data/nepal-districts.geojson')
            .then(res => res.json())
            .then(data => {
                L.geoJSON(data, {
                    style: {
                        color: "#3388ff",
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.1
                    },
                    onEachFeature: function (feature, layer) {
                        layer.on({
                            mouseover: function (e) {
                                var layer = e.target;
                                layer.setStyle({
                                    weight: 3,
                                    color: '#666',
                                    dashArray: '',
                                    fillOpacity: 0.7
                                });
                            },
                            mouseout: function (e) {
                                window.nepalMap.eachLayer(function (l) {
                                    if (l.feature === feature) {
                                        l.setStyle({
                                            weight: 2,
                                            color: "#3388ff",
                                            fillOpacity: 0.1
                                        });
                                    }
                                });
                            },
                            click: async function (e) {
                                const districtName = feature.properties.DISTRICT || feature.properties.name || "Unknown";

                                // Show loading state in popup
                                layer.bindPopup(`<div style="min-width:150px; text-align:center;"><strong>${districtName}</strong><br><span style="color:#64748b;">Analysing Risk...</span></div>`).openPopup();

                                // Reset and show container
                                const container = document.getElementById('mapAlertContainer');
                                const nameEl = document.getElementById('alertDistrictName');
                                const badgeEl = document.getElementById('alertRiskBadge');
                                const riskTextEl = document.getElementById('alertRiskText');
                                const crimesListEl = document.getElementById('alertRisingCrimes');

                                container.style.display = 'block';
                                container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

                                nameEl.textContent = districtName;
                                badgeEl.textContent = "Loading...";
                                badgeEl.className = "";
                                riskTextEl.textContent = "Retrieving crime forecast...";
                                crimesListEl.innerHTML = "";

                                try {
                                    // Fetch Prediction for Next Year (2082)
                                    const res = await fetch(`/api/predict?year=2082&province=&district=${encodeURIComponent(districtName)}`);
                                    const data = await res.json();

                                    if (data.status === 'error') {
                                        riskTextEl.textContent = "Data unavailable for this district.";
                                        return;
                                    }

                                    // Determine Status Class
                                    let statusClass = "badge-safe";
                                    let statusLabel = "Safe";
                                    if (data.safety_status.includes("Rising") || data.safety_status.includes("High")) {
                                        statusClass = "badge-high";
                                        statusLabel = "High Risk";
                                    } else if (data.safety_status.includes("Caution") || data.safety_status.includes("Mid")) {
                                        statusClass = "badge-mid";
                                        statusLabel = "Caution";
                                    }

                                    badgeEl.textContent = statusLabel;
                                    badgeEl.className = statusClass;
                                    riskTextEl.textContent = data.safety_status;

                                    // Updating Popup
                                    layer.setPopupContent(`<div style="min-width:150px; text-align:center;"><strong>${districtName}</strong><br><span class="${statusClass}" style="color:white; padding:2px 6px; border-radius:4px; font-size:0.8em;">${statusLabel}</span></div>`);

                                    // List Rising Crimes
                                    crimesListEl.innerHTML = "";
                                    if (data.rising_crimes && data.rising_crimes.length > 0) {
                                        data.rising_crimes.forEach(c => {
                                            crimesListEl.innerHTML += `
                                                <li style="display:flex; justify-content:space-between; background:white; padding:0.5rem; border-radius:4px; border:1px solid #f1f5f9;">
                                                    <span style="font-weight:600; color:#334155;">${c.crime_type}</span>
                                                    <span style="color:var(--danger-color); font-weight:bold;">+${c.trend.toFixed(1)}/yr</span>
                                                </li>
                                            `;
                                        });
                                    } else {
                                        crimesListEl.innerHTML = `<li style="color:#64748b; font-style:italic;">No rising crime trends detected.</li>`;
                                    }

                                } catch (err) {
                                    console.error("Alert fetch failed:", err);
                                    riskTextEl.textContent = "Failed to load risk analysis.";
                                }

                                // Fetch Police Stations
                                const stationsBody = document.getElementById('policeStationsBody');
                                stationsBody.innerHTML = '<tr><td colspan="2" style="padding:1rem; text-align:center; color:#94a3b8;">Loading directories...</td></tr>';

                                try {
                                    const resPol = await fetch(`/api/stations?district=${encodeURIComponent(districtName)}`);
                                    const stations = await resPol.json();

                                    stationsBody.innerHTML = '';
                                    if (stations && stations.length > 0) {
                                        stations.forEach(s => {
                                            stationsBody.innerHTML += `
                                                <tr style="border-bottom:1px solid #f1f5f9;">
                                                    <td style="padding:0.75rem; font-weight:500;">${s.name}</td>
                                                    <td style="padding:0.75rem; color:var(--primary-color);">
                                                        <i class="fas fa-phone-alt"></i> ${s.phone}
                                                    </td>
                                                </tr>
                                            `;
                                        });
                                    } else {
                                        stationsBody.innerHTML = '<tr><td colspan="2" style="padding:1rem; text-align:center; color:#94a3b8;">No contact information available for this district.</td></tr>';
                                    }
                                } catch (e) {
                                    console.error("Stations fetch failed:", e);
                                    stationsBody.innerHTML = '<tr><td colspan="2" style="padding:1rem; text-align:center; color:var(--danger-color);">Error loading contacts.</td></tr>';
                                }
                            }
                        });
                    }
                }).addTo(window.nepalMap);
            })
            .catch(err => console.error("Error loading GeoJSON:", err));

        window.toggleChartType = (type) => {
            state.currentChartType = type;
            if (type === 'pie') {
                elements.btnPie.classList.add('active');
                elements.btnBar.classList.remove('active');
            } else {
                elements.btnBar.classList.add('active');
                elements.btnPie.classList.remove('active');
            }
            renderMainView();
        };
    }

    function setupFilters() {
        // --- Main Crime Filters ---
        elements.mainYear.addEventListener('change', e => state.filters.main.year = e.target.value);
        elements.mainProvince.addEventListener('change', async e => {
            state.filters.main.province = e.target.value;
            await updateDistricts(state.filters.main.province, elements.mainDistrict);
        });
        elements.mainDistrict.addEventListener('change', e => state.filters.main.district = e.target.value.trim());

        elements.mainSearchBtn.addEventListener('click', async () => {
            await fetchMainDataWithFilters();
        });

        window.resetMainFilters = () => {
            elements.mainYear.value = "";
            elements.mainProvince.value = "";
            elements.mainDistrict.value = "";
            state.filters.main = { year: '', province: '', district: '' };
            updateDistricts('', elements.mainDistrict);
            fetchMainDataWithFilters();
        };

        // --- Demographics Filters ---
        elements.demoYear.addEventListener('change', e => state.filters.demo.year = e.target.value);
        elements.demoProvince.addEventListener('change', e => state.filters.demo.province = e.target.value);

        elements.demoSearchBtn.addEventListener('click', () => {
            updateDemoDashboard();
        });

        window.resetDemoFilters = () => {
            elements.demoYear.value = "";
            elements.demoProvince.value = "";
            state.filters.demo = { year: '', province: '' };
            updateDemoDashboard();
        };

        // --- Police Filters ---
        elements.polYear.addEventListener('change', e => state.filters.police.year = e.target.value);
        elements.polProvince.addEventListener('change', e => state.filters.police.province = e.target.value);

        elements.polSearchBtn.addEventListener('click', () => {
            updatePoliceDashboard();
        });

        window.resetPolFilters = () => {
            elements.polYear.value = "";
            elements.polProvince.value = "";
            state.filters.police = { year: '', province: '' };
            updatePoliceDashboard();
        };

        // --- Prediction Filters ---
        elements.predYear.addEventListener('change', e => state.filters.prediction.year = e.target.value);
        elements.predProvince.addEventListener('change', async e => {
            state.filters.prediction.province = e.target.value;
            state.filters.prediction.district = ''; // RESET DISTRICT
            await updateDistricts(state.filters.prediction.province, elements.predDistrict);
        });
        elements.predDistrict.addEventListener('change', e => state.filters.prediction.district = e.target.value);

        elements.predBtn.addEventListener('click', async () => {
            await fetchPrediction();
        });

        window.resetPredFilters = () => {
            elements.predYear.value = "2082";
            state.filters.prediction.year = "2082";
            elements.predProvince.value = "";
            state.filters.prediction.province = "";
            elements.predDistrict.innerHTML = '<option value="">Select District</option>';
            state.filters.prediction.district = "";
            elements.predictionResults.style.display = 'none';
        };
    }

    async function updateDistricts(province, dropdownElement) {
        dropdownElement.innerHTML = '<option value="">Select District</option>';
        if (!province) return;

        try {
            // Correctly use the API endpoint that supports province filtering
            const res = await fetch(`/api/districts?province=${encodeURIComponent(province)}`);
            const districts = await res.json();
            console.log(`DEBUG updateDistricts for ${province}:`, districts);

            // Explicitly clear again just to be paranoid
            dropdownElement.innerHTML = '<option value="">Select District</option>';

            districts.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d;
                dropdownElement.appendChild(opt);
            });
        } catch (e) {
            console.error("Error fetching districts:", e);
        }
    }

    function populateDropdowns(selectElement, options) {
        if (!options) return;
        // retain the first 'Select X' option if it exists, or just clear
        // Simplified: Clear everything and let caller handle default? 
        // Better: Keep the first option if it has empty value
        const firstOpt = selectElement.querySelector('option[value=""]');
        selectElement.innerHTML = '';
        if (firstOpt) selectElement.appendChild(firstOpt);

        options.forEach(optVal => {
            const opt = document.createElement('option');
            opt.value = optVal;
            opt.textContent = optVal;
            selectElement.appendChild(opt);
        });
    }

    async function fetchAllData() {
        try {
            // Initial load for detailed views
            const [demRes, polRes] = await Promise.all([
                fetch('/api/crime/detailed'),
                fetch('/api/police')
            ]);
            state.demographicsData = await demRes.json();
            state.policeData = await polRes.json();

            // SAVE GLOBAL COPIES
            state.globalPoliceData = [...state.policeData];

            // Only fetch global main data for "Combined" view stats
            const mainRes = await fetch('/api/crime/main');
            state.globalMainData = await mainRes.json();

            // Allow stats to be fetched globally too
            const statsRes = await fetch('/api/dashboard/stats');
            state.globalStats = await statsRes.json();

        } catch (error) { console.error("Error fetching initial data:", error); }
    }

    async function fetchMainDataWithFilters() {
        const params = new URLSearchParams();
        if (state.filters.main.year) params.append('year', state.filters.main.year);
        if (state.filters.main.province) params.append('province', state.filters.main.province);
        if (state.filters.main.district) params.append('district', state.filters.main.district);
        const queryString = '?' + params.toString();

        try {
            const res = await fetch('/api/crime/main' + queryString);
            state.mainData = await res.json();
            updateMainDashboard();
        } catch (error) { console.error(error); }
    }

    function updateMainDashboard() {
        try {
            renderMainView();
        } catch (e) {
            console.error("Error rendering Main View:", e);
            elements.mainCrimeInsight.innerHTML = `<div class="error-msg">Error loading analysis: ${e.message}</div>`;
        }
    }

    function updateDemoDashboard() {
        let filtered = state.demographicsData || [];
        if (state.filters.demo.year) {
            filtered = filtered.filter(d => d.Year == state.filters.demo.year);
        }
        if (state.filters.demo.province) {
            filtered = filtered.filter(d => d.Province && d.Province.includes(state.filters.demo.province));
        }
        renderDemographicsView(filtered);
    }

    function updatePoliceDashboard() {
        let filtered = state.policeData || [];
        if (state.filters.police.year) {
            filtered = filtered.filter(d => d.Year == state.filters.police.year);
        }
        if (state.filters.police.province) {
            filtered = filtered.filter(d => {
                const reg = d.Region || d.Province;
                return reg && reg.includes(state.filters.police.province);
            });
        }
        renderPoliceView(filtered);
    }

    function renderCombinedView(mainData, polData, stats) {
        console.log("Rendering Combined View...", {
            mainDataLen: mainData ? mainData.length : 0,
            polDataLen: polData ? polData.length : 0,
            sampleMain: mainData ? mainData[0] : null,
            stats: stats
        });
        if (!mainData || !polData) {
            console.warn("Missing data for combined view");
            return;
        }

        // NORMALIZE DATA (Fail-safe for key variations)
        const normalizedMain = mainData.map(d => ({
            province: d.Province || d.province || 'Unknown',
            district: d.District || d.district || 'Unknown',
            year: d.Year || d.year || 'Unknown',
            cases: d.Total_Cases || d.total_cases || d.Cases || 0
        }));

        const normalizedPol = polData.map(d => ({
            province: d.Region || d.Province || d.province || 'Unknown',
            opened: d.Opened_Cases || d.opened_cases || d.Opened || 0,
            closed: d.Closed_Cases || d.closed_cases || d.Closed || 0
        }));

        // 1. Header Stats
        if (stats) {
            elements.combTotalCases.textContent = (stats.total_crime_cases || 0).toLocaleString();
            elements.combClearanceRate.textContent = (stats.clearance_rate || 0) + '%';
            elements.combTopCrime.textContent = stats.top_crime_type || '-';
            elements.combActiveCases.textContent = (stats.opened_cases || 0).toLocaleString();
        }

        // 2. Crime vs Police Ratio (Removed)

        // 3. High Risk Areas
        const disCounts = {};
        // 3. High Risk Areas & Trend (Removed)

        // 4. Province-wise Trend Chart (Multi-Line) - Re-added
        const provMap = {};
        const allYears = new Set();

        normalizedMain.forEach(d => {
            if (d.year && d.province) {
                allYears.add(d.year);
                if (!provMap[d.province]) provMap[d.province] = {};
                provMap[d.province][d.year] = (provMap[d.province][d.year] || 0) + d.cases;
            }
        });

        const sortedYears = Array.from(allYears).sort();
        const provinces = Object.keys(provMap).sort();

        // --- DYNAMIC TREND ANALYSIS (Fiscal Year) ---
        let analysisHtml = "Data is insufficient for a separate annual analysis.";

        if (sortedYears.length > 0) {
            analysisHtml = '<ul style="padding-left: 1.2rem; margin: 0;">';

            // Loop through ALL years
            for (let i = 0; i < sortedYears.length; i++) {
                const curYear = sortedYears[i];
                const prevYear = i > 0 ? sortedYears[i - 1] : null; // Handle first year

                let totalCur = 0, totalPrev = 0;
                let maxIncreaseProv = null, maxIncreaseVal = -Infinity;
                let maxDecreaseProv = null, maxDecreaseVal = 0;
                let highestProv = null, highestVal = -Infinity;

                provinces.forEach(p => {
                    const c = provMap[p][curYear] || 0;
                    totalCur += c;

                    // Hotspot
                    if (c > highestVal) { highestVal = c; highestProv = p; }

                    if (prevYear) {
                        const prev = provMap[p][prevYear] || 0;
                        totalPrev += prev;
                        const d = c - prev;
                        if (d > 0 && d > maxIncreaseVal) { maxIncreaseVal = d; maxIncreaseProv = p; }
                        if (d < 0 && Math.abs(d) > maxDecreaseVal) { maxDecreaseVal = Math.abs(d); maxDecreaseProv = p; }
                    }
                });

                // Label Construction (e.g., 2076/77 -> 76/77)
                // If format is YYYY/YY, slice(2) gives YY/YY. If YYYY, slice(2) gives YY.
                // Robust check:
                const yearLabel = String(curYear).length > 4 ? String(curYear).slice(2) : curYear;

                let itemText = `<strong>${yearLabel}</strong>: <br>`;
                itemText += `<span style="color:#475569; font-size:0.9em;">`;

                itemText += `Reported incidents: <strong>${totalCur.toLocaleString()}</strong>. `;
                itemText += `Highest volume: <strong>${highestProv}</strong> (${highestVal}). `;

                if (prevYear) {
                    const totalDiff = totalCur - totalPrev;
                    const totalPct = totalPrev > 0 ? ((totalDiff / totalPrev) * 100).toFixed(1) : 0;
                    const natDirection = totalDiff >= 0 ? "increased" : "decreased";
                    const arrow = totalDiff >= 0 ? "↑" : "↓";
                    const natColor = totalDiff >= 0 ? "var(--danger-color)" : "var(--success-color)";

                    itemText += `<br>Trend: Nationwide <span style="color:${natColor}; font-weight:bold;">${natDirection} by ${Math.abs(totalPct)}% ${arrow}</span>. `;

                    if (maxIncreaseProv) {
                        itemText += `Sharpest spike in <strong>${maxIncreaseProv}</strong> (+${maxIncreaseVal}). `;
                    }
                } else {
                    itemText += `<br><em>Baseline year.</em>`;
                }

                itemText += `</span>`;

                // Detailed Breakdown for All Provinces
                itemText += `<div style="margin-top:4px; font-size:0.85em; color:#64748b; display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 4px;">`;
                provinces.forEach(p => {
                    const c = provMap[p][curYear] || 0;
                    let diffHtml = "";
                    if (prevYear) {
                        const prev = provMap[p][prevYear] || 0;
                        const d = c - prev;
                        const sign = d > 0 ? "+" : "";
                        const col = d > 0 ? "var(--danger-color)" : (d < 0 ? "var(--success-color)" : "#64748b");
                        diffHtml = ` (<span style="color:${col}">${sign}${d}</span>)`;
                    }
                    itemText += `<span><strong>${p}</strong>: ${c}${diffHtml}</span>`;
                });
                itemText += `</div>`;

                analysisHtml += `<li style="margin-bottom: 0.8rem; line-height:1.4;">${itemText}</li>`;
            }
            analysisHtml += "</ul>";
        }

        const trendEl = document.getElementById('trendAnalysis');
        if (trendEl) trendEl.innerHTML = analysisHtml;
        // -----------------------------

        // Distinct colors for 7 provinces
        const colors = [
            '#ef4444', '#f97316', '#f59e0b', '#10b981',
            '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899'
        ];

        const datasets = provinces.map((p, idx) => {
            const data = sortedYears.map(y => provMap[p][y] || 0);
            return {
                label: p,
                data: data,
                borderColor: colors[idx % colors.length],
                backgroundColor: 'transparent',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 4,
                pointHoverRadius: 6
            };
        });

        const ctxTrend = document.getElementById('trendChart').getContext('2d');
        if (state.charts['trendChart']) state.charts['trendChart'].destroy();

        state.charts['trendChart'] = new Chart(ctxTrend, {
            type: 'line',
            data: {
                labels: sortedYears,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20 } },
                    tooltip: { mode: 'index', intersect: false, backgroundColor: 'rgba(15, 23, 42, 0.9)' }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#e2e8f0' },
                        title: { display: true, text: 'Total Cases' }
                    },
                    x: {
                        grid: { display: false },
                        title: { display: true, text: 'Year' }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    function renderMainView() {
        const crimeCounts = {};
        if (state.allCrimeTypes) {
            state.allCrimeTypes.forEach(t => crimeCounts[t] = 0);
        }

        if (state.mainData) {
            state.mainData.forEach(d => crimeCounts[d.crime_type] = (crimeCounts[d.crime_type] || 0) + d.total_cases);
        }

        const entries = Object.entries(crimeCounts);
        let summaryText = "No data available for selected filters.";

        if (entries.length > 0) {
            entries.sort((a, b) => b[1] - a[1]);

            // Top 3 Most Reported
            const top3 = entries.slice(0, 3).filter(e => e[1] > 0);
            let top3Html = '';
            if (top3.length > 0) {
                top3Html = top3.map((e, i) =>
                    `<div><span style="color:#64748b; font-size:0.9em;">Rank ${i + 1}:</span> <strong>${e[0]}</strong> (${e[1].toLocaleString()})</div>`
                ).join('');
            } else {
                top3Html = 'None';
            }

            const chartEntries = entries.filter(e => e[1] > 0);

            // Limited Zero Cases
            const nonZero = entries.filter(e => e[1] > 0);
            const least = nonZero.length > 0 ? nonZero[nonZero.length - 1] : ['None', 0];
            const zeros = entries.filter(e => e[1] === 0).map(e => e[0]);

            let zeroText = 'None (All crime types present)';
            let zeroColor = '#94a3b8';
            if (zeros.length > 0) {
                // Show only first 3, no "others" count
                zeroText = zeros.slice(0, 3).join(', ');
                zeroColor = '#10b981';
            }

            summaryText = `
                <div style="margin-bottom:0.5rem; border-bottom:1px solid #e2e8f0; padding-bottom:0.5rem;">
                    <div style="margin-bottom:0.3rem;"><strong>Top Reported Crimes:</strong></div>
                    ${top3Html}
                </div>
                <div style="margin-bottom:0.5rem; border-bottom:1px solid #e2e8f0; padding-bottom:0.5rem;">
                    <strong>Least Reported:</strong> <span style="color:#f59e0b">${least[1] > 0 ? `${least[0]} (${least[1].toLocaleString()} cases)` : 'N/A'}</span>
                </div>
                <div>
                    <strong>Zero Reported Cases (Safe):</strong> <span style="color:${zeroColor}; font-size:0.9rem;">${zeroText}</span>
                </div>
            `;

            elements.mainCrimeInsight.innerHTML = summaryText;

            const labels = chartEntries.map(e => e[0]);
            const data = chartEntries.map(e => e[1]);
            const colors = generateColors(labels.length);
            createChart('crimeTypeChart', state.currentChartType, labels, data, 'Cases', colors);
        } else {
            elements.mainCrimeInsight.innerHTML = summaryText;
            // Clear chart
            if (state.charts['crimeTypeChart']) state.charts['crimeTypeChart'].destroy();
        }
    }

    function renderDemographicsView(data) {
        if (!data || data.length === 0) {
            resetDemographicsUI();
            return;
        }

        let f = 0, m = 0, u = 0;
        let edu = {}, rel = {}, age = {};

        data.forEach(d => {
            f += d.Victim_Female || 0;
            m += d.Victim_Male || 0;
            u += d.Victim_Unknown || 0;

            ['Victim_Edu_Illiterate', 'Victim_Edu_Literate', 'Victim_Edu_SchoolLevel', 'Victim_Edu_Plus2', 'Victim_Edu_BachelorPlus'].forEach(k => {
                edu[k.replace('Victim_Edu_', '')] = (edu[k.replace('Victim_Edu_', '')] || 0) + (d[k] || 0);
            });
            ['Relationship_Family', 'Relationship_Relative', 'Relationship_Neighbor', 'Relationship_Teacher', 'Relationship_Acquaintance', 'Relationship_Stranger', 'Relationship_Unknown'].forEach(k => {
                rel[k.replace('Relationship_', '')] = (rel[k.replace('Relationship_', '')] || 0) + (d[k] || 0);
            });
            ['Victim_Age_Group_lte_10', 'Victim_Age_Group_11_14', 'Victim_Age_Group_15_16', 'Victim_Age_Group_17_18', 'Victim_Age_Group_19_25', 'Victim_Age_Group_26_35', 'Victim_Age_Group_36_45', 'Victim_Age_Group_46_59', 'Victim_Age_Group_60_plus'].forEach(k => {
                age[k.replace('Victim_Age_Group_', '')] = (age[k.replace('Victim_Age_Group_', '')] || 0) + (d[k] || 0);
            });
        });

        const totalGender = f + m + u;
        elements.demFemaleCount.textContent = f;
        elements.demFemalePct.textContent = totalGender ? ((f / totalGender) * 100).toFixed(1) + '%' : '0%';
        elements.demMaleCount.textContent = m;
        elements.demMalePct.textContent = totalGender ? ((m / totalGender) * 100).toFixed(1) + '%' : '0%';
        elements.demUnknownCount.textContent = u;
        elements.demUnknownPct.textContent = totalGender ? ((u / totalGender) * 100).toFixed(1) + '%' : '0%';

        elements.eduStatsContainer.innerHTML = '';
        Object.entries(edu).forEach(([k, v]) => elements.eduStatsContainer.innerHTML += createStatRow(k, v));
        createChart('eduChart', 'bar', Object.keys(edu), Object.values(edu), 'Victim Education', generateColors(Object.keys(edu).length));

        elements.relStatsContainer.innerHTML = '';
        Object.entries(rel).forEach(([k, v]) => elements.relStatsContainer.innerHTML += createStatRow(k, v));
        createChart('relChart', 'doughnut', Object.keys(rel), Object.values(rel), 'Relationship', generateColors(Object.keys(rel).length));

        elements.ageStatsContainer.innerHTML = '';
        const ageLabels = Object.keys(age).map(k => k.replace('lte_', '≤').replace('_plus', '+').replace(/_/g, '-'));
        Object.entries(age).forEach(([k, v]) => elements.ageStatsContainer.innerHTML += createStatRow(k.replace('lte_', '≤').replace('_plus', '+').replace(/_/g, '-'), v));
        createChart('ageChart', 'bar', ageLabels, Object.values(age), 'Age Distribution', generateColors(ageLabels.length));

        let knownSum = 0, count = 0;
        data.forEach(d => { if (d.Known_Offender_Percent != undefined) { knownSum += d.Known_Offender_Percent; count++; } });
        elements.knownOffenderVal.textContent = count ? (knownSum / count).toFixed(1) + '%' : '0%';
    }

    function renderPoliceView(data) {
        if (!data || data.length === 0) {
            elements.polOpenedVal.textContent = 0;
            elements.polClosedVal.textContent = 0;
            return;
        }

        let opened = 0, closed = 0;
        data.forEach(d => {
            opened += d.Opened_Cases || 0;
            closed += d.Closed_Cases || 0;
        });

        elements.polOpenedVal.textContent = opened.toLocaleString();
        elements.polClosedVal.textContent = closed.toLocaleString();
        elements.polOpenedPct.textContent = "Total Registered";
        elements.polClosedPct.textContent = opened > 0 ? ((closed / opened) * 100).toFixed(1) + '% Clearance' : '0%';
        createChart('openedClosedChart', 'doughnut', ['Closed', 'Pending/Active'], [closed, Math.max(0, opened - closed)], 'Cases', ['#10b981', '#f59e0b']);
    }

    function resetDemographicsUI() {
        elements.demFemaleCount.textContent = '-';
        elements.demFemalePct.textContent = '-';
        elements.demMaleCount.textContent = '-';
        elements.demMalePct.textContent = '-';
        elements.demUnknownCount.textContent = '-';
        elements.demUnknownPct.textContent = '-';

        const msg = '<div class="no-data-msg" style="padding:1rem; color:#64748b; text-align:center;">No demographics data available for this selection.</div>';
        elements.eduStatsContainer.innerHTML = msg;
        elements.relStatsContainer.innerHTML = msg;
        elements.ageStatsContainer.innerHTML = msg;
    }


    function createStatRow(label, value) {
        return `<div style="background:var(--background-gray); padding:0.5rem; border-radius:4px; display:flex; justify-content:space-between; align-items:center; border:1px solid var(--border-color);">
            <span style="font-size:0.85rem; color:var(--text-secondary);">${label}</span>
            <span style="font-weight:bold; color:var(--text-primary);">${value}</span>
        </div>`;
    }

    function generateColors(count) {
        const palette = [
            '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            '#ec4899', '#06b6d4', '#f97316', '#6366f1', '#14b8a6'
        ];
        return Array(count).fill().map((_, i) => palette[i % palette.length]);
    }

    function createChart(canvasId, type, labels, data, label, bgColors) {
        try {
            let canvas = document.getElementById(canvasId);
            if (!canvas) return;

            // 1. Global Registry Nuke: Iterate and destroy ANY chart on this canvas
            Object.values(Chart.instances).forEach(chart => {
                if (chart.canvas.id === canvasId) {
                    chart.destroy();
                }
            });

            // 2. Direct Canvas Check
            const existingChart = Chart.getChart(canvas);
            if (existingChart) existingChart.destroy();

            // 3. State Tracker
            if (state.charts[canvasId]) {
                state.charts[canvasId].destroy();
                state.charts[canvasId] = null;
            }

            // 4. Element Replacement (The Nuclear Option)
            const newCanvas = document.createElement('canvas');
            newCanvas.id = canvasId;
            newCanvas.className = canvas.className;
            newCanvas.style.cssText = canvas.style.cssText;

            if (canvas.parentNode) {
                canvas.parentNode.replaceChild(newCanvas, canvas);
            }
            canvas = newCanvas;

            const ctx = canvas.getContext('2d');
            state.charts[canvasId] = new Chart(ctx, {
                type: type,
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: data,
                        backgroundColor: bgColors || generateColors(data.length),
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: type === 'bar' ? { display: false } : { position: 'bottom', labels: { color: '#94a3b8' } }
                    },
                    scales: type === 'bar' ? {
                        y: { beginAtZero: true, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    } : {}
                }
            });
        } catch (err) {
            console.warn("Chart error suppressed:", err);
        }
    }

    async function fetchPrediction() {
        const { year, province, district } = state.filters.prediction;
        console.log("Prediction Request:", { year, province, district });
        if (!year) {
            alert("Please select a target year.");
            return;
        }

        elements.predBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Predicting...';

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ year, province, district })
            });
            const data = await res.json();

            if (data.error) throw new Error(data.error);
            renderPredictionView(data);

        } catch (e) {
            alert("Prediction Error: " + e.message);
        } finally {
            elements.predBtn.innerHTML = 'Predict Crime Trends';
        }
    }

    function renderPredictionView(data) {
        elements.predictionResults.style.display = 'block';

        // Safety Card
        elements.predSafetyStatus.textContent = data.safety_status;
        elements.predTargetYearLabel.textContent = data.target_year;
        elements.predTotalCount.textContent = data.total_predicted_cases.toLocaleString();

        // Color coding for status
        if (data.safety_status.includes("Rising")) {
            elements.safetyCard.style.borderLeftColor = 'var(--danger-color)';
            elements.predSafetyStatus.style.color = 'var(--danger-color)';
        } else if (data.safety_status.includes("Safer")) {
            elements.safetyCard.style.borderLeftColor = 'var(--success-color)';
            elements.predSafetyStatus.style.color = 'var(--success-color)';
        } else {
            elements.safetyCard.style.borderLeftColor = '#f59e0b';
            elements.predSafetyStatus.style.color = '#f59e0b';
        }

        // Rising Crimes
        elements.risingCrimesList.innerHTML = '';
        if (data.rising_crimes && data.rising_crimes.length > 0) {
            data.rising_crimes.forEach(c => {
                const trend = c.trend > 0 ? `+${c.trend.toFixed(1)}/yr` : `${c.trend.toFixed(1)}/yr`;
                elements.risingCrimesList.innerHTML += `
                    <div style="background:var(--background-gray); padding:0.75rem; border-radius:4px; display:flex; justify-content:space-between; align-items:center; border-left:3px solid var(--danger-color);">
                        <div>
                            <div style="color:var(--text-primary); font-weight:600;">${c.crime_type}</div>
                            <div style="font-size:0.8rem; color:var(--text-secondary);">Predicted: ${c.predicted_cases} cases</div>
                        </div>
                        <div style="color:var(--danger-color); font-weight:bold; font-size:0.9rem;">
                            <i class="fas fa-arrow-up"></i> ${trend}
                        </div>
                    </div>
                `;
            });
        } else {
            elements.risingCrimesList.innerHTML = '<div style="color:#94a3b8; font-style:italic;">No crimes predicted to rise significantly.</div>';
        }

        // Chart
        const labels = data.detailed_predictions.slice(0, 10).map(d => d.crime_type);
        const values = data.detailed_predictions.slice(0, 10).map(d => d.predicted_cases);
        createChart('predictionChart', 'bar', labels, values, 'Predicted Cases', null);
    }

    init();
});

function createChart(canvasId, type, labels, data, label, bgColors) {
    try {
        let canvas = document.getElementById(canvasId);
        if (!canvas) return;

        // 1. Global Registry Nuke: Iterate and destroy ANY chart on this canvas
        // This handles cases where ID lookup fails but the chart object exists
        Object.values(Chart.instances).forEach(chart => {
            if (chart.canvas.id === canvasId) {
                chart.destroy();
            }
        });

        // 2. Direct Canvas Check
        const existingChart = Chart.getChart(canvas);
        if (existingChart) existingChart.destroy();

        // 3. State Tracker
        if (state.charts[canvasId]) {
            state.charts[canvasId].destroy();
            state.charts[canvasId] = null;
        }

        // 4. Element Replacement (The Nuclear Option)
        const newCanvas = document.createElement('canvas');
        newCanvas.id = canvasId;
        newCanvas.className = canvas.className;
        newCanvas.style.cssText = canvas.style.cssText;

        if (canvas.parentNode) {
            canvas.parentNode.replaceChild(newCanvas, canvas);
        }
        canvas = newCanvas;

        const ctx = canvas.getContext('2d');
        state.charts[canvasId] = new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: bgColors || generateColors(data.length),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: type === 'bar' ? { display: false } : { position: 'bottom', labels: { color: '#94a3b8' } }
                },
                scales: type === 'bar' ? {
                    y: { beginAtZero: true, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                } : {}
            }
        });
    } catch (err) {
        console.warn("Chart error suppressed:", err);
    }
}
