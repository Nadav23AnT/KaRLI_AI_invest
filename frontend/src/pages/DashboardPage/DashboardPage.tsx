import { useEffect, useState } from "react"
import { AppSidebar } from "@/Components/app-sidebar"
import { ChartAreaInteractive } from "@/Components/chart-area-interactive"
import { DataTable } from "@/Components/data-table"
import { SectionCards } from "@/Components/section-cards"
import { SiteHeader } from "@/Components/site-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"

import data from "@/app/dashboard/data.json"

export default function DashboardPage() {
  const [sectionData, setSectionData] = useState<{
    accountInfo: {
      account_blocked: boolean
      balance_asof: string
      cash: string
      created_at: string
      currency: string
      equity: string
      status: string
      trading_blocked: boolean
    }
    cashBeingUsedForTrading: number
    portfolioHistory: {
      latest_equity: number
      latest_profit_loss: number
      latest_profit_loss_pct: number
      latest_timestamp: number
    }
  } | null>(null)

  const username = localStorage.getItem("username")
  const isAuthenticated = localStorage.getItem("isAuthenticated") === "true"

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (isAuthenticated && username) {
          const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/summary`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ username }),
          })

          if (!response.ok) {
            throw new Error("Failed to fetch data")
          }

          const result = await response.json()

          // Transform API response to match SectionCards expected props
          setSectionData({
            accountInfo: result.accountInfo,
            cashBeingUsedForTrading: parseFloat(result.accountInfo.equity) - parseFloat(result.accountInfo.cash),
            portfolioHistory: {
              latest_equity: result.portfolioHistory.latest_equity,
              latest_profit_loss: result.portfolioHistory.latest_profit_loss,
              latest_profit_loss_pct: result.portfolioHistory.latest_profit_loss_pct,
              latest_timestamp: result.portfolioHistory.latest_timestamp,
            },
          })
        }
      } catch (error) {
        console.error("Error fetching data:", error)
      }
    }

    fetchData()
  }, [])

  return (
    <SidebarProvider>
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              {/* Ensure data is loaded before rendering SectionCards */}
              {sectionData ? <SectionCards {...sectionData} /> : <p>Loading...</p>}
              <div className="px-4 lg:px-6">
                <ChartAreaInteractive />
              </div>
              <DataTable data={data} />
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
