FROM node:22-alpine AS base
ARG APP_HOME=/app

FROM base AS deps
RUN apk add --no-cache libc6-compat
# sets relative path, all subsequennt path references are based off this
WORKDIR ${APP_HOME}

# copy package.json into 
COPY package.json package-lock.json ./
# clean install
RUN npm ci

FROM base AS build
WORKDIR ${APP_HOME}
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# nextjs default data collection disabled
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

RUN npm run build

FROM base AS run
WORKDIR ${APP_HOME}

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# copies public files (images, fonts, pdfs, logos, robots.xtx, etc)
COPY --from=build /app/public ./public
# copy next app
COPY --from=build --chown=nextjs:nodejs /app/.next/standalone ./
# copies static files 
COPY --from=build --chown=nextjs:nodejs /app/.next/static ./.next/static  

USER nextjs

EXPOSE 3000

ENV PORT 3000

ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]