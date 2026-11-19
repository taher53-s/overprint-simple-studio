package studio;

import java.util.*;

/** Output-only JSON serializer; requests use standard URL-encoded forms. */
public final class Json {
    public static String encode(Object o) {
        if (o == null) return "null";
        if (o instanceof String s) return quote(s);
        if (o instanceof Number n) {
            if (!Double.isFinite(n.doubleValue())) throw new IllegalArgumentException("Non-finite JSON number");
            return n.toString();
        }
        if (o instanceof Boolean) return o.toString();
        if (o instanceof Map<?,?> m) {
            StringJoiner j = new StringJoiner(",", "{", "}");
            m.forEach((k,v) -> j.add(quote(k.toString()) + ":" + encode(v)));
            return j.toString();
        }
        if (o instanceof Iterable<?> list) {
            StringJoiner j = new StringJoiner(",", "[", "]");
            for (Object v : list) j.add(encode(v));
            return j.toString();
        }
        throw new IllegalArgumentException("Unsupported JSON type: " + o.getClass());
    }
    private static String quote(String s) {
        StringBuilder out = new StringBuilder("\"");
        for (char c : s.toCharArray()) switch(c) {
            case '"' -> out.append("\\\"");
            case '\\' -> out.append("\\\\");
            case '\n' -> out.append("\\n");
            case '\r' -> out.append("\\r");
            case '\t' -> out.append("\\t");
            default -> { if (c < 32) out.append(String.format("\\u%04x", (int)c)); else out.append(c); }
        }
        return out.append('"').toString();
    }
}
