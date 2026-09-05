// UVR5 模型选型指南 - 图表
(function () {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  // --- 模型数量分布 ---
  var fam = echarts.init(document.getElementById('chart-families'), null, { renderer: 'svg' });
  fam.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      axisPointer: { type: 'shadow' }
    },
    grid: { left: 8, right: 16, top: 12, bottom: 8, containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: { color: muted },
      splitLine: { lineStyle: { color: rule } }
    },
    yAxis: {
      type: 'category',
      data: ['Demucs', 'MDX23C', 'VR-ARCH', 'MDX-NET', 'Roformer'],
      axisLabel: { color: ink, fontWeight: 600 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: [4, 5, 28, 34, 86],
      barWidth: 20,
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: function (p) {
          return p.dataIndex === 4 ? accent : accent2;
        }
      },
      label: {
        show: true,
        position: 'right',
        color: ink,
        fontWeight: 700
      }
    }]
  });
  window.addEventListener('resize', function () { fam.resize(); });

  // --- 按用途模型数量 ---
  var purp = echarts.init(document.getElementById('chart-purposes'), null, { renderer: 'svg' });
  purp.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      axisPointer: { type: 'shadow' }
    },
    grid: { left: 8, right: 14, top: 12, bottom: 8, containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: { color: muted },
      splitLine: { lineStyle: { color: rule } }
    },
    yAxis: {
      type: 'category',
      data: [
        '人声·伴奏分离',
        '去混响',
        '降噪',
        '卡拉OK',
        '伴奏专精',
        '人声专精',
        '鼓组分离',
        '人声修复',
        '男女声分离',
        '齿音·气息',
        '去回声',
        '人群',
        '渗漏抑制'
      ],
      axisLabel: { color: ink },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: [20, 10, 3, 4, 28, 26, 3, 5, 2, 2, 3, 1, 1],
      barWidth: 14,
      itemStyle: { borderRadius: [0, 5, 5, 0], color: accent },
      label: {
        show: true,
        position: 'right',
        color: ink,
        fontWeight: 700
      }
    }]
  });
  window.addEventListener('resize', function () { purp.resize(); });
})();