#!/bin/bash

# Docker Run Script for Telegram Channels Manager Bot
# ===================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           Telegram Channels Manager Bot - Docker            ║"
    echo "║                    نص تشغيل Docker                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_help() {
    echo -e "${YELLOW}Usage: $0 [COMMAND] [OPTIONS]${NC}"
    echo ""
    echo "Commands:"
    echo "  build        - Build Docker image"
    echo "  start        - Start bot services"
    echo "  stop         - Stop bot services"
    echo "  restart      - Restart bot services"
    echo "  logs         - Show bot logs"
    echo "  status       - Show services status"
    echo "  shell        - Open shell in bot container"
    echo "  clean        - Clean up containers and volumes"
    echo "  monitoring   - Start with monitoring (Prometheus + Grafana)"
    echo "  web          - Start with web interface (Nginx)"
    echo "  full         - Start with all services"
    echo "  setup        - Interactive setup"
    echo "  health       - Check services health"
    echo ""
    echo "Options:"
    echo "  --no-cache   - Build without cache"
    echo "  --follow     - Follow logs in real time"
    echo "  --force      - Force operation"
    echo "  --help       - Show this help"
}

check_requirements() {
    echo -e "${BLUE}فحص المتطلبات...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker غير مثبت${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose غير مثبت${NC}"
        exit 1
    fi
    
    # Check .env file
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️ ملف .env غير موجود، سيتم إنشاؤه من المثال${NC}"
        if [ -f .env.example ]; then
            cp .env.example .env
            echo -e "${GREEN}✅ تم إنشاء .env من .env.example${NC}"
            echo -e "${YELLOW}⚠️ يرجى تحرير ملف .env قبل التشغيل${NC}"
        else
            echo -e "${RED}❌ ملف .env.example غير موجود${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ جميع المتطلبات متوفرة${NC}"
}

build_image() {
    echo -e "${BLUE}بناء Docker image...${NC}"
    
    CACHE_OPTION=""
    if [[ "$*" == *"--no-cache"* ]]; then
        CACHE_OPTION="--no-cache"
        echo -e "${YELLOW}⚠️ البناء بدون cache${NC}"
    fi
    
    docker-compose build $CACHE_OPTION telegram-bot
    
    echo -e "${GREEN}✅ تم بناء الـ image بنجاح${NC}"
}

start_services() {
    local profile=""
    
    case "$1" in
        "monitoring")
            profile="--profile monitoring"
            echo -e "${BLUE}تشغيل البوت مع المراقبة...${NC}"
            ;;
        "web")
            profile="--profile web"
            echo -e "${BLUE}تشغيل البوت مع واجهة الويب...${NC}"
            ;;
        "full")
            profile="--profile monitoring --profile web"
            echo -e "${BLUE}تشغيل البوت مع جميع الخدمات...${NC}"
            ;;
        *)
            echo -e "${BLUE}تشغيل البوت فقط...${NC}"
            ;;
    esac
    
    docker-compose $profile up -d
    
    echo -e "${GREEN}✅ تم تشغيل الخدمات${NC}"
    echo ""
    
    # Show running containers
    docker-compose ps
    
    # Show access URLs
    echo ""
    echo -e "${YELLOW}🔗 روابط الوصول:${NC}"
    echo "• البوت: منشط ويعمل في الخلفية"
    
    if [[ "$profile" == *"web"* ]]; then
        echo "• واجهة الويب: http://localhost"
    fi
    
    if [[ "$profile" == *"monitoring"* ]]; then
        echo "• Prometheus: http://localhost:9090"
        echo "• Grafana: http://localhost:3000 (admin/admin123)"
    fi
}

stop_services() {
    echo -e "${BLUE}إيقاف الخدمات...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ تم إيقاف جميع الخدمات${NC}"
}

restart_services() {
    echo -e "${BLUE}إعادة تشغيل الخدمات...${NC}"
    docker-compose restart
    echo -e "${GREEN}✅ تم إعادة تشغيل الخدمات${NC}"
}

show_logs() {
    local follow_option=""
    
    if [[ "$*" == *"--follow"* ]]; then
        follow_option="-f"
        echo -e "${BLUE}عرض السجلات مع المتابعة المباشرة...${NC}"
    else
        echo -e "${BLUE}عرض آخر السجلات...${NC}"
    fi
    
    docker-compose logs $follow_option --tail=100
}

show_status() {
    echo -e "${BLUE}حالة الخدمات:${NC}"
    echo ""
    
    docker-compose ps
    
    echo ""
    echo -e "${BLUE}استخدام الموارد:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose ps -q 2>/dev/null) 2>/dev/null || echo "لا توجد حاويات تعمل"
}

open_shell() {
    echo -e "${BLUE}فتح shell في حاوية البوت...${NC}"
    
    if docker-compose ps telegram-bot | grep -q "Up"; then
        docker-compose exec telegram-bot bash
    else
        echo -e "${RED}❌ حاوية البوت غير تعمل${NC}"
        exit 1
    fi
}

clean_up() {
    local force=""
    
    if [[ "$*" == *"--force"* ]]; then
        force="--force"
    else
        echo -e "${YELLOW}⚠️ هذا سيحذف جميع الحاويات والـ volumes${NC}"
        read -p "هل أنت متأكد؟ (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "تم الإلغاء"
            exit 0
        fi
    fi
    
    echo -e "${BLUE}تنظيف الحاويات والـ volumes...${NC}"
    
    docker-compose down -v --remove-orphans
    docker-compose --profile monitoring --profile web down -v --remove-orphans
    
    # Remove dangling images
    docker image prune -f
    
    echo -e "${GREEN}✅ تم التنظيف${NC}"
}

interactive_setup() {
    echo -e "${BLUE}الإعداد التفاعلي${NC}"
    echo "=================="
    
    # Check if .env exists and ask to reconfigure
    if [ -f .env ]; then
        echo -e "${YELLOW}ملف .env موجود بالفعل${NC}"
        read -p "هل تريد إعادة الإعداد؟ (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "تم تخطي الإعداد"
        else
            python3 setup_bot.py
        fi
    else
        python3 setup_bot.py
    fi
    
    # Ask about build
    echo ""
    read -p "هل تريد بناء الـ Docker image؟ (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        build_image
    fi
    
    # Ask about services
    echo ""
    echo "اختر نوع التشغيل:"
    echo "1) البوت فقط"
    echo "2) البوت + المراقبة"
    echo "3) البوت + واجهة الويب"
    echo "4) جميع الخدمات"
    
    read -p "اختيارك (1-4): " -n 1 -r
    echo
    
    case $REPLY in
        1) start_services ;;
        2) start_services "monitoring" ;;
        3) start_services "web" ;;
        4) start_services "full" ;;
        *) echo "اختيار غير صحيح، سيتم تشغيل البوت فقط"; start_services ;;
    esac
}

check_health() {
    echo -e "${BLUE}فحص صحة الخدمات...${NC}"
    echo ""
    
    # Check if containers are running
    if ! docker-compose ps telegram-bot | grep -q "Up"; then
        echo -e "${RED}❌ البوت غير يعمل${NC}"
        return 1
    fi
    
    # Check health status
    health_status=$(docker inspect --format='{{.State.Health.Status}}' telegram-channels-bot 2>/dev/null || echo "no-health-check")
    
    case $health_status in
        "healthy")
            echo -e "${GREEN}✅ البوت يعمل بصحة جيدة${NC}"
            ;;
        "unhealthy")
            echo -e "${RED}❌ البوت غير سليم${NC}"
            ;;
        "starting")
            echo -e "${YELLOW}⏳ البوت قيد البدء...${NC}"
            ;;
        *)
            echo -e "${YELLOW}⚠️ لا يوجد فحص صحة${NC}"
            ;;
    esac
    
    # Check Redis
    if docker-compose ps redis | grep -q "Up"; then
        redis_health=$(docker exec telegram-bot-redis redis-cli ping 2>/dev/null || echo "FAILED")
        if [ "$redis_health" = "PONG" ]; then
            echo -e "${GREEN}✅ Redis يعمل بصحة جيدة${NC}"
        else
            echo -e "${RED}❌ Redis غير سليم${NC}"
        fi
    fi
    
    echo ""
    show_status
}

# Main script
main() {
    print_banner
    
    case "${1:-}" in
        "build")
            check_requirements
            build_image "$@"
            ;;
        "start")
            check_requirements
            start_services "${2:-}"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            show_logs "$@"
            ;;
        "status")
            show_status
            ;;
        "shell")
            open_shell
            ;;
        "clean")
            clean_up "$@"
            ;;
        "monitoring")
            check_requirements
            start_services "monitoring"
            ;;
        "web")
            check_requirements
            start_services "web"
            ;;
        "full")
            check_requirements
            start_services "full"
            ;;
        "setup")
            check_requirements
            interactive_setup
            ;;
        "health")
            check_health
            ;;
        "help"|"--help"|"-h")
            print_help
            ;;
        "")
            echo -e "${YELLOW}⚠️ لم يتم تحديد أمر${NC}"
            echo ""
            print_help
            ;;
        *)
            echo -e "${RED}❌ أمر غير معروف: $1${NC}"
            echo ""
            print_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"