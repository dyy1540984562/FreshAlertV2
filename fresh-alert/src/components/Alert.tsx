import { Button } from "@/components/ui/button"

interface AlertProps {
  type: 'error' | 'success';
  title: string;
  message: string;
  onClose: () => void;
}

export function Alert({ type, title, message, onClose }: AlertProps) {
  const bgColor = type === 'error' ? 'bg-red-100' : 'bg-green-100'
  const textColor = type === 'error' ? 'text-red-800' : 'text-green-800'

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
      <div className={`${bgColor} p-6 rounded-lg shadow-lg max-w-md w-full`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>{title}</h2>
        <p className={`text-lg mb-4 ${textColor}`}>{message}</p>
        <div className="flex justify-end">
          <Button onClick={onClose}>关闭</Button>
        </div>
      </div>
    </div>
  )
}