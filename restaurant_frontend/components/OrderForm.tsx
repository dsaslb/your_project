import { useState } from "react";
import { Button } from "@/components/ui/button";

export type OrderFormValues = {
  item: string;
  quantity: number;
  reason: string;
};

type OrderFormProps = {
  initialValues?: OrderFormValues;
  onSubmit: (values: OrderFormValues) => void;
  onCancel: () => void;
};

export function OrderForm({ initialValues, onSubmit, onCancel }: OrderFormProps) {
  const [item, setItem] = useState(initialValues?.item || "");
  const [quantity, setQuantity] = useState(initialValues?.quantity || 1);
  const [reason, setReason] = useState(initialValues?.reason || "");

  return (
    <form
      onSubmit={e => {
        e.preventDefault();
        onSubmit({ item, quantity, reason });
      }}
      className="space-y-4"
      aria-label="발주 등록/수정 폼"
    >
      <div>
        <label className="block mb-1 text-sm">품목</label>
        <input
          className="w-full border rounded px-2 py-1"
          value={item}
          onChange={e => setItem(e.target.value)}
          required
        />
      </div>
      <div>
        <label className="block mb-1 text-sm">수량</label>
        <input
          type="number"
          className="w-full border rounded px-2 py-1"
          value={quantity}
          min={1}
          onChange={e => setQuantity(Number(e.target.value))}
          required
        />
      </div>
      <div>
        <label className="block mb-1 text-sm">요청사유</label>
        <input
          className="w-full border rounded px-2 py-1"
          value={reason}
          onChange={e => setReason(e.target.value)}
          required
        />
      </div>
      <div className="flex gap-2 justify-end">
        <Button type="button" variant="ghost" onClick={onCancel}>취소</Button>
        <Button type="submit">등록</Button>
      </div>
    </form>
  );
} 