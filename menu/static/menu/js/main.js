(function () {
  "use strict";

  // The order form template embeds {item_id: price} as a JSON script tag.
  // We read it here so JavaScript knows each item's price.
  var mapEl = document.getElementById("price-map");
  if (!mapEl) return;  // not on the order form page, do nothing

  var prices = JSON.parse(mapEl.textContent || "{}");

  function money(n) {
    return "RWF" + (Math.round(n * 100) / 100).toFixed(2);
  }

  function recalc() {
    var grand = 0;
    document.querySelectorAll("#lines .line").forEach(function (line) {
      var sel = line.querySelector("select.line-item");
      var qtyInput = line.querySelector("input.line-qty");
      var totalCell = line.querySelector(".line-total");
      if (!sel || !qtyInput || !totalCell) return;

      var price = parseFloat(prices[sel.value] || "0");
      var qty = parseInt(qtyInput.value || "0", 10);
      var lineTotal = price * (isNaN(qty) ? 0 : qty);

      totalCell.textContent = money(lineTotal);
      grand += lineTotal;
    });

    var grandEl = document.getElementById("running-total");
    if (grandEl) grandEl.textContent = money(grand);
  }

  // One listener on the container handles all current and future rows.
  var container = document.getElementById("lines");
  if (container) {
    container.addEventListener("change", recalc);
    container.addEventListener("input", recalc);
  }

  recalc();  // run once on page load (covers the edit page with existing data)
})();