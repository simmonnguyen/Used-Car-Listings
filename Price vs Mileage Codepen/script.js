const DATA_URL = "https://simmonnguyen.github.io/Used-Car-Listings/used_car_listings.json";

// Choose the two columns to visualize:
const COL_PRICE   = "price";   // bars will use this (height)
const COL_MILEAGE = "mileage"; // circles will use this (size/color/position)

const W = 760, H = 420, M = {t:28, r:24, b:48, l:60};
const innerW = W - M.l - M.r, innerH = H - M.t - M.b;

const svg = d3.select("#viz");
const g = svg.append("g").attr("transform", `translate(${M.l},${M.t})`);

// Axes groups
const gx = g.append("g").attr("class", "axis x")
  .attr("transform", `translate(0,${innerH})`);
const gy = g.append("g").attr("class", "axis y");

// Load data
d3.json(DATA_URL).then(raw => {
  // Basic clean-up: keep rows that have numeric price & mileage
  const data = (raw || [])
    .map(d => ({
      ...d,
      price: +d[COL_PRICE],
      mileage: +d[COL_MILEAGE],
      label: d.make && d.model ? `${d.make} ${d.model}` : (d.model || d.make || d.vin || "item")
    }))
    .filter(d => Number.isFinite(d.price) && Number.isFinite(d.mileage))
    .slice(0, 30); // keep it small & fast

  // Scales
  const x = d3.scaleBand()
    .domain(d3.range(data.length))
    .range([0, innerW])
    .padding(0.2);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.price) * 1.1]).nice()
    .range([innerH, 0]);

  const r = d3.scaleSqrt() // circle radius from mileage
    .domain(d3.extent(data, d => d.mileage))
    .range([3, 14]);

  const color = d3.scaleSequential(d3.extent(data, d => d.mileage),
    d3.interpolateTurbo);

  // Axes
  gx.call(d3.axisBottom(x).tickFormat(i => i + 1).tickSizeOuter(0));
  gy.call(d3.axisLeft(y).ticks(6).tickFormat(d3.format("$,.0f")));

  // Bars (first column: price)
  const bars = g.selectAll("rect.bar")
    .data(data)
    .join("rect")
      .attr("class", "bar")
      .attr("x", (_, i) => x(i))
      .attr("y", innerH)               // start from bottom
      .attr("width", x.bandwidth())
      .attr("height", 0)               // animate in
      .attr("rx", 8)
      .attr("fill", "#60a5fa");

  bars.transition().duration(900).ease(d3.easeCubicOut)
    .attr("y", d => y(d.price))
    .attr("height", d => innerH - y(d.price));

  // Circles (second column: mileage) positioned near bars’ tops
  const dots = g.selectAll("circle.dot")
    .data(data)
    .join("circle")
      .attr("class", "dot")
      .attr("cx", (_, i) => x(i) + x.bandwidth()/2)
      .attr("cy", d => y(d.price) - 12) // close to bar top
      .attr("r", 0)                     // animate in
      .attr("fill", d => color(d.mileage))
      .attr("stroke", "#0006")
      .attr("stroke-width", 1);

  dots.transition().delay((_,i)=>100+i*10).duration(700).ease(d3.easeBackOut.overshoot(1.6))
    .attr("r", d => r(d.mileage));

  // Optional: simple labels under bars (index)
  g.selectAll("text.label")
    .data(data)
    .join("text")
      .attr("class", "label")
      .attr("x", (_, i) => x(i) + x.bandwidth()/2)
      .attr("y", innerH + 28)
      .text((d,i) => `#${i+1}`);

  // Hover tooltip (very light)
  const tip = d3.select("body").append("div")
    .style("position","fixed").style("pointer-events","none")
    .style("background","#0b1022").style("color","#e5e7eb")
    .style("border","1px solid #334155").style("padding","6px 8px")
    .style("border-radius","8px").style("font","12px system-ui")
    .style("opacity",0);

  function showTip(event, d, i) {
    tip.style("opacity", 1)
      .html(
        `<strong>${d.label}</strong><br>
         Price: $${d3.format(",")(d.price)}<br>
         Mileage: ${d3.format(",")(d.mileage)}`
      )
      .style("left", (event.clientX + 12) + "px")
      .style("top", (event.clientY + 12) + "px");
  }
  function hideTip() { tip.style("opacity", 0); }

  bars.on("mousemove", (e,d,i)=>showTip(e,d,i)).on("mouseleave", hideTip);
  dots.on("mousemove", (e,d,i)=>showTip(e,d,i)).on("mouseleave", hideTip);

}).catch(err => {
  console.error("Failed to load data:", err);
  const msg = svg.append("text")
    .attr("x", W/2).attr("y", H/2)
    .attr("text-anchor","middle").attr("fill","#e5e7eb")
    .text("Could not load data. Check your GitHub Pages URL.");
});
