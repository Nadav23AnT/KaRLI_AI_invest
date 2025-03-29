import { IconTrendingDown, IconTrendingUp } from "@tabler/icons-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function SectionCards({
  accountInfo,
  cashBeingUsedForTrading,
  portfolioHistory,
}: {
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
}) {
  return (
    <div className="grid grid-cols-1 gap-4 px-4 lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      {/* Equity & Cash Balance Card */}
      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Account Equity & Cash</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums">
            {accountInfo.equity} {accountInfo.currency} 
          </CardTitle>
          <div className="text-lg text-muted-foreground">
            Current Cash Balance: {accountInfo.cash} {accountInfo.currency}
          </div>
        </CardHeader>
        <CardFooter className="flex-col items-start text-sm">
          <div className="text-muted-foreground">
            Last updated: {accountInfo.balance_asof}
          </div>
        </CardFooter>
      </Card>

      {/* Cash Being Used for Trading */}
      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Cash in Trading</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums">
            {cashBeingUsedForTrading.toFixed(3)} {accountInfo.currency}
          </CardTitle>
        </CardHeader>
        <CardFooter className="flex-col items-start text-sm">
          <div className="text-muted-foreground">Current trading exposure</div>
        </CardFooter>
      </Card>

      {/* Portfolio Profit/Loss */}
      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Portfolio Profit/Loss</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums">
            {portfolioHistory.latest_profit_loss.toFixed(2)} {accountInfo.currency} 
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              {portfolioHistory.latest_profit_loss >= 0 ? (
                <>
                  <IconTrendingUp />
                  {portfolioHistory.latest_profit_loss_pct.toFixed(2)}%
                </>
              ) : (
                <>
                  <IconTrendingDown />
                  {portfolioHistory.latest_profit_loss_pct.toFixed(2)}%
                </>
              )}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start text-sm">
          <div className="text-muted-foreground">
            Last update: {new Date(portfolioHistory.latest_timestamp * 1000).toLocaleString()}
          </div>
        </CardFooter>
      </Card>

      {/* Account Status */}
      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Account Status</CardDescription>
          <CardTitle
            className={`text-2xl font-semibold tabular-nums ${
              accountInfo.account_blocked || accountInfo.trading_blocked || accountInfo.status !== "ACTIVE" ? "text-red-500" : "text-green-500"
            }`}
          >
            {accountInfo.account_blocked || accountInfo.trading_blocked || accountInfo.status !== "ACTIVE" ? "Not Active" : "Active"}
          </CardTitle>
        </CardHeader>
        <CardFooter className="flex-col items-start text-sm">
          <div className="text-muted-foreground">
            Trading Blocked: {accountInfo.trading_blocked ? "Yes" : "No"}
          </div>
          <div className="text-muted-foreground">
            Account Blocked: {accountInfo.account_blocked ? "Yes" : "No"}
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
