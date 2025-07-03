export function Alert({ message, type = "info", ...props }: { message: string; type?: "info" | "success" | "error" } & React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div role="alert" aria-live="assertive" className={`px-4 py-2 rounded shadow text-white ${type === "error" ? "bg-red-500" : type === "success" ? "bg-green-500" : "bg-blue-500"}`} {...props}>
      {message}
    </div>
  );
} 