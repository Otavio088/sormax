document.addEventListener('DOMContentLoaded', function () {
    // Grafico de produção
    const chartDataProduction = variableNames.map((name, index) => ({
        name: name,
        y: quantitiesProduction[index],
        price: variablePrices[index],
    }));
    Highcharts.chart('chart', {
        chart: {
            type: 'pie'
        },
        title: {
            text: 'Visão Geral de Produção'
        },
        tooltip: {
            formatter: function () {
                const total = this.point.y * this.point.price; // Cálculo correto do total
                return `<b>${this.point.name}</b><br>
                    <b>Quantidade a produzir:</b> ${this.point.y} unidades<br>
                    <b>Valor unitário:</b> R$ ${this.point.price.toFixed(2)}<br>
                    <b>Valor total:</b> R$ ${total.toFixed(2)}`;
            }
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.y} unidades'
                }
            }
        },
        credits: {
            enabled: false
        },
        series: [{
            colorByPoint: true,
            data: chartDataProduction
        }]
    });

    // Grafico de restrições
    const chartDataRestrictions = restrictionsNames.map((name, index) => ({
        name: name,
        available: availableRestrictions[index],
        used: usedRestrictions[index]
    }));
    Highcharts.chart('chart_restrictions', {
        chart: {
            type: 'bar'
        },
        title: {
            text: 'Comparação de Restrições'
        },
        xAxis: {
            categories: restrictionsNames,
            title: {
                text: 'Restrições'
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Quantidade'
            }
        },
        tooltip: {
            shared: true,
            formatter: function () {
                return `<b>${this.points[0].key}</b><br>
                <b>Disponível:</b> ${this.points[0].y}<br>
                <b>Utilizado:</b> ${this.points[1].y}`;
            }
        },
        plotOptions: {
            series: {
                dataLabels: {
                    enabled: true
                }
            }
        },
        credits: {
            enabled: false
        },
        series: [{
            name: 'Disponível',
            data: chartDataRestrictions.map(item => item.available),
            color: '#2b908f'
        }, {
            name: 'Utilizado',
            data: chartDataRestrictions.map(item => item.used),
            color: '#f45b5b'
        }]
    });
});