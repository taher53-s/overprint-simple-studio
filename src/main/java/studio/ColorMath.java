package studio;

/** sRGB -> CIE XYZ (D65) -> CIELAB; Euclidean Delta E 1976. No printer profile. */
public final class ColorMath {
    public static String hex(String value) {
        String s = value.trim().toUpperCase(java.util.Locale.ROOT);
        if (!s.matches("#[0-9A-F]{6}"))
            throw new IllegalArgumentException("Use six-digit colors such as #ED622F.");
        return s;
    }
    private static double linear(int channel) {
        double c = channel / 255.0;
        return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    }
    private static double f(double t) {
        double d = 6.0 / 29;
        return t > d*d*d ? Math.cbrt(t) : t / (3*d*d) + 4.0/29;
    }
    public static double[] lab(String color) {
        String h = hex(color);
        double r = linear(Integer.parseInt(h.substring(1,3),16));
        double g = linear(Integer.parseInt(h.substring(3,5),16));
        double b = linear(Integer.parseInt(h.substring(5,7),16));
        double x = f((.4124564*r + .3575761*g + .1804375*b)/.95047);
        double y = f(.2126729*r + .7151522*g + .0721750*b);
        double z = f((.0193339*r + .1191920*g + .9503041*b)/1.08883);
        return new double[]{116*y-16, 500*(x-y), 200*(y-z)};
    }
    public static double distance(double[] a, double[] b) {
        return Math.sqrt(Math.pow(a[0]-b[0],2)+Math.pow(a[1]-b[1],2)+Math.pow(a[2]-b[2],2));
    }
}
