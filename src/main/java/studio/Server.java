package studio;

import com.sun.net.httpserver.*;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.Executors;

public final class Server {
    private static final Path WEB = Path.of("web").toAbsolutePath().normalize();
    public static void main(String[] args) throws Exception {
        int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "3000"));
        String host = System.getenv().getOrDefault("HOST", "127.0.0.1");
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--port") && i+1 < args.length) port = Integer.parseInt(args[++i]);
            else if (args[i].equals("--host") && i+1 < args.length) host = args[++i];
            else if (!args[i].equals("--strictPort")) throw new IllegalArgumentException("Unknown server argument: " + args[i]);
        }
        HttpServer server = HttpServer.create(new InetSocketAddress(host, port), 0);
        server.createContext("/", Server::handle);
        server.setExecutor(Executors.newFixedThreadPool(8));
        server.start();
        System.out.println("OVERPRINT running at http://" + host + ":" + port);
    }
    private static void handle(HttpExchange x) throws IOException {
        try {
            x.getResponseHeaders().set("X-Content-Type-Options", "nosniff");
            x.getResponseHeaders().set("Cache-Control", "no-store");
            String path = x.getRequestURI().getPath();
            if (path.equals("/api/health") && x.getRequestMethod().equals("GET")) {
                json(x, 200, Map.of("status", "ok", "backend", "Java", "project", "OVERPRINT"));
            } else if (path.equals("/api/plan")) {
                if (!x.getRequestMethod().equals("POST")) {
                    x.getResponseHeaders().set("Allow", "POST");
                    json(x,405,Map.of("error","Use POST for planning.")); return;
                }
                String type = x.getRequestHeaders().getFirst("Content-Type");
                if (type == null || !type.startsWith("application/x-www-form-urlencoded")) {
                    json(x,415,Map.of("error","Send a URL-encoded form.")); return;
                }
                byte[] bytes = x.getRequestBody().readNBytes(65537);
                if (bytes.length > 65536) { json(x,413,Map.of("error","Request exceeds 64 KB.")); return; }
                Map<String,String> form = new LinkedHashMap<>();
                for (String pair : new String(bytes, StandardCharsets.UTF_8).split("&")) {
                    String[] parts = pair.split("=", 2);
                    String key = URLDecoder.decode(parts[0],StandardCharsets.UTF_8);
                    if (form.containsKey(key)) throw new IllegalArgumentException("Repeated parameter: " + key);
                    form.put(key, parts.length == 1 ? "" : URLDecoder.decode(parts[1],StandardCharsets.UTF_8));
                }
                json(x,200,Planner.plan(form));
            } else if (path.equals("/api/benchmarks") && x.getRequestMethod().equals("GET")) {
                Path p = Path.of("results/benchmarks.json");
                if (!Files.exists(p)) json(x,404,Map.of("error","Run ./run.sh benchmark to generate evidence."));
                else send(x,200,"application/json; charset=utf-8",Files.readAllBytes(p));
            } else if (path.startsWith("/api/")) json(x,404,Map.of("error","Endpoint not found."));
            else {
                if (!x.getRequestMethod().equals("GET")) { json(x,405,Map.of("error","Use GET for files.")); return; }
                Path file = WEB.resolve(path.equals("/") ? "index.html" : path.substring(1)).normalize();
                if (!file.startsWith(WEB) || !Files.isRegularFile(file)) { json(x,404,Map.of("error","File not found.")); return; }
                String name = file.toString();
                String mime = name.endsWith(".vtt") ? "text/vtt; charset=utf-8" : name.endsWith(".mp4") ? "video/mp4" : name.endsWith(".jpg") ? "image/jpeg" : name.endsWith(".html") ? "text/html; charset=utf-8" : name.endsWith(".css") ? "text/css" : name.endsWith(".js") ? "text/javascript" : name.endsWith(".svg") ? "image/svg+xml" : name.endsWith(".woff2") ? "font/woff2" : "application/octet-stream";
                send(x,200,mime,Files.readAllBytes(file));
            }
        } catch (NumberFormatException e) {
            json(x,400,Map.of("error","Check numeric costs, tolerance, review count, press limit and seed."));
        } catch (IllegalArgumentException e) {
            json(x,400,Map.of("error",e.getMessage() == null ? "Invalid input." : e.getMessage()));
        } catch (Exception e) {
            e.printStackTrace(); json(x,500,Map.of("error","Planning failed. See the server log."));
        } finally { x.close(); }
    }
    private static void json(HttpExchange x, int status, Object value) throws IOException {
        send(x,status,"application/json; charset=utf-8",Json.encode(value).getBytes(StandardCharsets.UTF_8));
    }
    private static void send(HttpExchange x, int status, String type, byte[] data) throws IOException {
        x.getResponseHeaders().set("Content-Type",type);
        x.sendResponseHeaders(status,data.length);
        x.getResponseBody().write(data);
    }
}
