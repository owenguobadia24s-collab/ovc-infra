import { describe, expect, it } from "vitest";
import { msToTimestamptzStart2H, parseExport } from "../src/index";

describe("TradingView MIN helpers", () => {
  it("parses pipe-delimited export strings into a map", () => {
    const parsed = parseExport("a=1|sym=GBPUSD|bar_close_ms=1736860800000|bid=XYZ");
    expect(parsed).toEqual({
      a: "1",
      sym: "GBPUSD",
      bar_close_ms: "1736860800000",
      bid: "XYZ",
    });
  });

  it("computes 2H block_start from bar_close_ms", () => {
    const barCloseMs = Date.UTC(2025, 0, 14, 4, 0, 0);
    const blockStart = msToTimestamptzStart2H(barCloseMs);
    expect(blockStart).toBe("2025-01-14T02:00:00.000Z");
  });
});
