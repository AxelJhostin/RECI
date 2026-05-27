# Reci

Robot físico de reciclaje inteligente para el campus de la PUCE Sede Manabí.

Plataforma móvil de dos compartimentos (vidrio / plástico) que se desplaza entre puntos fijos del campus, clasifica residuos con visión artificial + sistema experto, y se acompaña de una app móvil con gamificación y recompensas.

## Subsistemas

- **Reci físico** — plataforma rodante con Raspberry Pi 4 + ESP32, cámara, servos, OLED, LEDs, audio.
- **Reci cloud** — backend en Supabase + Next.js API routes (PostgreSQL, Auth, Realtime, Storage).
- **Reci app** — PWA en Next.js + Tailwind: mapa del campus, llamar al robot, historial, cupones.

## Equipo

| Integrante | Rol principal |
| --- | --- |
| Paula Márquez | Project Manager + Lead Developer (App & Cloud) |
| Axel Hernández | Lead IA + Sistema Experto |
| Leonela Sornoza | Hardware + Testing |
| Andrea Campaña | Hardware + Testing |

## Contexto académico

- Universidad: PUCE Sede Manabí — Ingeniería de Software, 5to semestre
- Periodo: PAO 2026-01
- Duración: 16 semanas
- Materias integradoras: Análisis y Circuitos Eléctricos, Sistemas Expertos, Gestión de Proyectos, Tecnologías de Plataforma

Ver [`docs/ACTA.md`](docs/ACTA.md) para el acta de constitución completa.
