"use client"

import * as React from "react"
import ReactCalendar, { CalendarProps as ReactCalendarProps } from "react-calendar"
import "react-calendar/dist/Calendar.css"
import { cn } from "@/lib/utils"

export type CalendarProps = ReactCalendarProps & {
  className?: string
}

function Calendar({ className, ...props }: CalendarProps) {
  return (
    <div className={cn("rounded-md border bg-background p-3", className)}>
      <ReactCalendar
        {...props}
        className={cn("w-full border-none bg-transparent", className)}
        prevLabel={<span className="text-lg">‹</span>}
        nextLabel={<span className="text-lg">›</span>}
        formatShortWeekday={(locale, date) =>
          ["일", "월", "화", "수", "목", "금", "토"][date.getDay()]
        }
        tileClassName={({ date, view }) =>
          view === "month"
            ? "h-9 w-9 flex items-center justify-center rounded-md text-sm hover:bg-accent hover:text-accent-foreground focus:bg-primary focus:text-primary-foreground"
            : undefined
        }
      />
    </div>
  )
}
Calendar.displayName = "Calendar"

export { Calendar }
