// Configuração Global Chart.js (GovTech Analítico)
Chart.register(ChartDataLabels);
Chart.defaults.color = '#64748b';
Chart.defaults.font.family = 'Inter';
Chart.defaults.font.weight = '500';
Chart.defaults.scale.grid.color = 'rgba(0, 0, 0, 0.04)';

const colors = {
    blue: '#0f172a',
    indigo: '#4338ca',
    emerald: '#059669',
    amber: '#d97706',
    red: '#dc2626',
    teal: '#0d9488',
    slate: '#64748b'
};

const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toLocaleString('pt-BR');
};

// Configuração dos Rótulos de Dados (DataLabels)
Chart.defaults.set('plugins.datalabels', {
    color: '#0f172a',
    font: { weight: '600', family: 'Inter', size: 10 },
    align: 'top',
    anchor: 'end',
    offset: 2,
    formatter: function(value) {
        if(typeof value === 'number') {
            if (value >= 1000) return formatNumber(value);
            return (value % 1 === 0) ? value : value.toFixed(1) + '%';
        }
        return value;
    }
});

async function loadKPIs() {
    try {
        const res = await fetch('./dashboard/api_data/kpis.json');
        const data = await res.json();
        document.getElementById('kpi-escolas').textContent = formatNumber(data.total_escolas);
        document.getElementById('kpi-matriculas').textContent = formatNumber(data.total_matriculas);
        document.getElementById('kpi-eja').textContent = data.pct_eja + '%';
        document.getElementById('kpi-vuln').textContent = data.pct_vulneraveis + '%';
        document.getElementById('kpi-ano').textContent = data.ano_referencia;
    } catch (e) { console.error(e); }
}

async function loadTrendChart() {
    try {
        const res = await fetch('./dashboard/api_data/evasion_trend.json');
        const data = await res.json();
        const ctx = document.getElementById('trendChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Total Absoluto (Brasil)',
                    data: data.total,
                    borderColor: colors.indigo,
                    backgroundColor: 'rgba(67, 56, 202, 0.1)',
                    borderWidth: 3, fill: true, tension: 0.3,
                    pointRadius: 4, pointBackgroundColor: colors.indigo
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { x: { grid: { display: false } } }
            }
        });
    } catch (e) { console.error(e); }
}

async function loadStageChart() {
    try {
        const res = await fetch('./dashboard/api_data/stage_dropout.json');
        const data = await res.json();
        const ctx = document.getElementById('stageChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    { 
                        label: 'Retenção (%) no Ens. Médio', 
                        data: data.retencao_medio, 
                        borderColor: colors.amber,
                        backgroundColor: 'rgba(217, 119, 6, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 4,
                        pointBackgroundColor: colors.amber
                    }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { 
                    x: { grid: { display: false } },
                    y: { 
                        title: { display: true, text: 'Taxa de Retenção (%)' },
                        min: 0, max: 100
                    }
                }
            }
        });
    } catch (e) { console.error(e); }
}

async function loadUrbanRuralChart() {
    try {
        const res = await fetch('./dashboard/api_data/urban_rural.json');
        const data = await res.json();
        const ctx = document.getElementById('urbanRuralChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    { label: 'Urbana (Índice Base 100)', data: data.urbana, borderColor: colors.emerald, borderWidth: 3, tension: 0.2 },
                    { label: 'Rural (Índice Base 100)', data: data.rural, borderColor: colors.red, borderWidth: 3, borderDash: [5, 5], tension: 0.2 }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { 
                    x: { grid: { display: false } },
                    y: { title: { display: true, text: 'Variação Relativa (%)' } }
                }
            }
        });
    } catch (e) { console.error(e); }
}

// O VERDADEIRO IMPACTO DA INFRAESTRUTURA (VARIAÇÃO %)
async function loadInfraEvasionChart() {
    try {
        const res = await fetch('./dashboard/api_data/infra_evasion_rate.json');
        const data = await res.json();
        const ctx = document.getElementById('infraEvasionChart').getContext('2d');
        
        // Cores baseadas se o valor é negativo (vermelho/âmbar) ou positivo (verde)
        const bgColors = data.variacao.map(v => v < 0 ? colors.red : colors.emerald);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: `Crescimento/Queda % (${data.ano_base} vs ${data.ano_recente})`,
                    data: data.variacao,
                    backgroundColor: bgColors,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { 
                    x: { grid: { display: false } },
                    y: { title: { display: true, text: 'Variação % de Alunos' } }
                }
            }
        });
    } catch (e) { console.error(e); }
}

// O ABANDONO MASCULINO
async function loadGenderEvasionChart() {
    try {
        const res = await fetch('./dashboard/api_data/evasion_gender.json');
        const data = await res.json();
        const ctx = document.getElementById('genderEvasionChart').getContext('2d');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels, // ['Fundamental', 'Ensino Médio']
                datasets: [
                    { label: '% Meninos', data: data.masculino, backgroundColor: colors.indigo },
                    { label: '% Meninas', data: data.feminino, backgroundColor: colors.teal }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { x: { grid: { display: false } }, y: { min: 40, max: 60 } }
            }
        });
    } catch (e) { console.error(e); }
}

// DEMANDA SOCIAL EJA
async function loadEjaDemand() {
    try {
        const res = await fetch('./dashboard/api_data/social_demand_eja.json');
        const data = await res.json();
        
        // Gráfico de Linha Histórico
        const demandCtx = document.getElementById('ejaDemandChart').getContext('2d');
        new Chart(demandCtx, {
            type: 'line',
            data: {
                labels: data.historico.labels,
                datasets: [
                    { label: 'EJA - Demanda Social (Base 100)', data: data.historico.eja_index, borderColor: colors.red, backgroundColor: 'rgba(220,38,38,0.1)', borderWidth: 3, fill: true, tension: 0.3 },
                    { label: 'Ensino Médio Regular (Base 100)', data: data.historico.medio_index, borderColor: colors.amber, borderWidth: 3, borderDash: [4,4], tension: 0.3 }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { 
                    x: { grid: { display: false } },
                    y: { title: { display: true, text: 'Variação Relativa (%)' } }
                }
            }
        });

        // Gráfico de Raça EJA (Doughnut)
        const raceCtx = document.getElementById('ejaRaceChart').getContext('2d');
        new Chart(raceCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.raca_eja),
                datasets: [{
                    data: Object.values(data.raca_eja),
                    backgroundColor: [colors.amber, colors.indigo],
                    borderWidth: 0, hoverOffset: 8
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '70%',
                plugins: { legend: { position: 'bottom' } }
            }
        });
    } catch (e) { console.error(e); }
}

document.addEventListener('DOMContentLoaded', () => {
    loadKPIs();
    loadTrendChart();
    loadStageChart();
    loadUrbanRuralChart();
    loadInfraEvasionChart();
    loadGenderEvasionChart();
    loadEjaDemand();
});
